# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
CMSIS

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) is a
vendor-independent hardware abstraction layer for the Cortex-M processor
series and specifies debugger interfaces. The CMSIS enables consistent and
simple software interfaces to the processor for interface peripherals,
real-time operating systems, and middleware. It simplifies software
re-use, reducing the learning curve for new microcontroller developers
and cutting the time-to-market for devices.

http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php
"""

import glob
import os
import string
import sys

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
mcu = board.get("build.mcu", "")

if not mcu:
    sys.stderr.write("""Error: MCU not specified!  Cannot build without a recognized build.mcu specified.\n""")
    env.Exit(1)

env.SConscript("_bare.py")

CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_ROOT_DIR = platform.get_package_dir("framework-cmsis-atmelsam")
# The Atmel CMSIS path length can be different, e.g. "sam3u" all the way up to "saml21a1".  This means that
#we need to match the available /folders/ against the MCU part number to find the necessary folder with "startswith".
# Adding to this are SAM families with different revisions, e.g. "A/B/C/D/L", etc.  Any revision character is preceded
#with an underscore in the folder tree (e.g. "saml21_b"), means that we have to look at the end of the MCU part number
#to check for that character to identify the revision.  Also note that the revision character is not always the last
#character of the part number--and sometimes there can be multiple revision characters, in addition to non-revision
#suffix characters (e.g. "DU", where "U" is not a revision character).
CMSIS_ATMEL_CATEGORY = ""
folder_list = [f for f in glob.iglob('*', root_dir=CMSIS_ATMEL_ROOT_DIR) if not os.path.isfile(f) and mcu.startswith(f.partition("_")[0])]
print ("Matching MCU category list: ", folder_list)
if (len(folder_list) > 1):
    # Get the processor part number suffix
    p_suf = ""
    for i in range(len(mcu) - 1, 0, -1):
        if (mcu[i].isdigit()):
            p_suf = mcu[i + 1:]
            break
    p_suf = p_suf.removesuffix("u")      # some MCUs have a "U" suffix; not sure what it indicates.
    print("MCU suffix to match: ", p_suf)

    # Need to match up a suffix on the part number (if present) to determine the corresponding folder.
    for fm in folder_list:
        f_suf = fm.partition("_")[2]     # folder suffix (if present)
        print("Category '{}' suffix: {}".format(fm, f_suf))
        if (f_suf == p_suf):
            CMSIS_ATMEL_CATEGORY = fm
            break

if (CMSIS_ATMEL_CATEGORY == ""):
    # no match found above.  This may be a SAMC21 / SAMC21N-style difference: pick the longest path
    CMSIS_ATMEL_CATEGORY = max(folder_list, key=len)                            # "samc21n" > "samc21"...

assert (CMSIS_ATMEL_CATEGORY != ""), "Cannot find a CMSIS category for '%s'" % mcu
CMSIS_DEVICE_DIR = os.path.join(CMSIS_ATMEL_ROOT_DIR, CMSIS_ATMEL_CATEGORY)

def get_linker_script():
    LDSCRIPT_ROOT_PATH = os.path.join(CMSIS_DEVICE_DIR, "gcc", "gcc")           # /gcc/gcc/
    default_ldscript = os.path.join(LDSCRIPT_ROOT_PATH, "%s_flash.ld" % mcu)    # NOTE: "_sram.ld" also available
    if not os.path.isfile(default_ldscript):
        sys.stderr.write("""Error: Cannot find a linker script for '%s' MCU in CMSIS folder '%s'!\n""" % (mcu, LDSCRIPT_ROOT_PATH))
        env.Exit(1)

    # from a different ATSAM CMSIS script: allow adjusting the binary offset (bootloader, etc.)
    offset_address = board.get("build.offset", "0")
    if int(offset_address, 0) > 0:
        sys.stderr.write("""Error: Build offset '%s' detected.  Copy linker script '%s' to project folder, modify it, and specify it with "board_build.ldscript"\n""" % (offset_address, default_ldscript))
        env.Exit(1)

    return default_ldscript


#
# Allow using custom linker scripts
#
if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=get_linker_script())
else:
    cust_ldscript = board.get("build.ldscript", "")
    print("Using custom linker script '%s'" % cust_ldscript)
    env.Replace(LDSCRIPT_PATH=cust_ldscript)

#    ram = board.get("upload.maximum_ram_size", 0)
#    flash = board.get("upload.maximum_size", 0)

#
# Prepare build environment
#

# The final firmware is linked against standard library with two specifications:
# nano.specs - link against a reduced-size variant of libc
# nosys.specs - link against stubbed standard syscalls

env.Append(
    CPPPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Core", "Include"),    # generic CMSIS headers from "framework-cmsis"
        CMSIS_ATMEL_ROOT_DIR,                                   # for "samc.h", "samd.h", etc.
        os.path.join(CMSIS_DEVICE_DIR, "include")               # processor-specifics
    ],
)

# LINKFLAGS are already included in "bare.py" only for "samc" and "samd",
#causing an error when compiling if redefined.  We can't overwrite, otherwise
#compilation fails due to losing all other LINKFLAGS.
if ("samd" not in mcu) and ("samc" not in mcu):
    env.Append(
        LINKFLAGS=[
            "--specs=nano.specs",
            "--specs=nosys.specs"
        ]
    )


#
# Compile CMSIS sources
#

sources_path = os.path.join(CMSIS_DEVICE_DIR, "gcc")
# Find startup file.  Most have specifics (e.g. "startup_samc21g16a.c"),
#while some older ones may only have a family generic (e.g. "startup_samd10.c")
# Try the specific first. If not found, look for the generic.  We shan't include both.
startup_file = "startup_%s.c" % mcu.lower()
if not os.path.isfile(os.path.join(sources_path, "gcc", startup_file)):
    startup_file = "startup_%s.c" % CMSIS_ATMEL_CATEGORY.lower()
assert os.path.isfile(os.path.join(sources_path, "gcc", startup_file)), "Could not find startup file, either \"startup_%s.c\" or \"startup_%s.c\"" % (mcu.lower(), CMSIS_ATMEL_CATEGORY.lower())

env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkCMSIS"), sources_path,
    src_filter=[
        "-<*>",
        "+<%s>" % board.get("build.cmsis.system_file", "system_%s.c" % CMSIS_ATMEL_CATEGORY.lower()),
        "+<gcc/%s>" % board.get("build.cmsis.startup_file", startup_file)
    ]
)
