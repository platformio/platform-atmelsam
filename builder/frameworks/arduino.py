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
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://arduino.cc/en/Reference/HomePage
"""

from os import walk
from os.path import isdir, isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinosam")
FRAMEWORK_VERSION = platform.get_package_version("framework-arduinosam")
assert isdir(FRAMEWORK_DIR)

ARDUINO_VERSION = int(
    open(join(FRAMEWORK_DIR, "version.txt")).read().replace(".", "").strip())
CMSIS_DIRNAME = "CMSIS%s" % (
    "_ORG" if env.BoardConfig().get("build.core", "").endswith("_org") else "")

# USB flags
ARDUINO_USBDEFINES = [("ARDUINO", int(FRAMEWORK_VERSION.split(".")[1]))]
if "build.usb_product" in env.BoardConfig():
    ARDUINO_USBDEFINES += [
        ("USB_VID", env.BoardConfig().get("build.hwids")[0][0]),
        ("USB_PID", env.BoardConfig().get("build.hwids")[0][1]),
        ("USB_PRODUCT", '\\"%s\\"' %
         env.BoardConfig().get("build.usb_product", "").replace('"', "")),
        ("USB_MANUFACTURER", '\\"%s\\"' %
         env.BoardConfig().get("vendor", "").replace('"', ""))
    ]

env.Append(
    CPPDEFINES=ARDUINO_USBDEFINES,

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        join(FRAMEWORK_DIR, "system", CMSIS_DIRNAME, "CMSIS", "Include"),
        join(FRAMEWORK_DIR, "system", "libsam"),
        join(FRAMEWORK_DIR, "system", "libsam", "include"),
        join(FRAMEWORK_DIR, "system", CMSIS_DIRNAME, "Device", "ATMEL"),
        join(FRAMEWORK_DIR, "system", CMSIS_DIRNAME, "Device", "ATMEL",
             env.BoardConfig().get("build.mcu", "")[3:], "include"),
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "variants",
             env.BoardConfig().get("build.variant"), "linker_scripts", "gcc")
    ]
)

# search relative includes in lib SAM directories
core_dir = join(FRAMEWORK_DIR, "system", "libsam")
for root, _, files in walk(core_dir):
    for lib_file in files:
        file_path = join(root, lib_file)
        if not isfile(file_path):
            continue
        content = None
        content_changed = False
        with open(file_path) as fp:
            content = fp.read()
            if '#include "../' in content:
                content_changed = True
                content = content.replace('#include "../', '#include "')
            if not content_changed:
                continue
            with open(file_path, "w") as fp:
                fp.write(content)

#
# Lookup for specific core's libraries
#

BOARD_CORELIBDIRNAME = (
    "digispark" if "digispark" in env.BoardConfig().get("build.core", "")
    else env.BoardConfig().get("build.core", ""))
env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries", "__cores__", BOARD_CORELIBDIRNAME),
        join(FRAMEWORK_DIR, "libraries")
    ]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
))

if "sam3x8e" in env.BoardConfig().get("build.mcu", ""):
    env.Append(
        LIBPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )

    libs.append("sam_sam3x8e_gcc_rel")

env.Prepend(LIBS=libs)
