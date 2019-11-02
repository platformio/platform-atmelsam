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

import sys
import re
from glob import glob
from string import Template
from os.path import isdir, isfile, join, basename

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

env.SConscript("_bare.py")

PLATFORM_NAME = env.get("PIOPLATFORM")
FRAMEWORK_DIR = platform.get_package_dir("framework-cmsis")
assert isdir(FRAMEWORK_DIR)

MCU_FAMILY_SELECTORS = {
  'sam3a': r'^sam3a.*$',
  'sam3n': r'^sam3n.*$',
  'sam3s': r'^sam3s[^8]*$',
  'sam3sd8': r'^sam3sd?[8].?$',
  'sam3x': r'^sam3x.*$',
  'sam3u': r'^sam3u.*$',
  'sam3x': r'^(at91)?sam3x.*$',
  'sam4c32': r'^sam4c32.*$',
  'sam4cm32': r'^sam4cm.*32.*$',
  'sam4cm': r'^sam4cm[^3]*$',
  'sam4cp': r'^sam4cp.*$',
  'sam4c': r'^sam4c[^mp3]*$',
  'sam4e': r'^sam4e(.*[ce])?$',
  'sam4ecb': r'^sam4e\d+cb$',
  'sam4l4': r'^sam4l[cs][24][abc]$',
  'sam4l8': r'^sam4l[cs]8[abc]$',
  'sam4n': r'^sam4n.*$',
  'sam4sp': r'^sam4sp.*$',
  'sam4s': r'^sam4s[^p]*$',
  'samb11': r'^samb11$',
  'samc20': r'^samc20[^n]*$',
  'samc20n': r'^samc20n.*$',
  'samc21': r'^samc21[^n]*$',
  'samc21n': r'^samc21n.*$',
  'samd09': r'^samd09.*$',
  'samd10': r'^samd10.*$',
  'samd11': r'^samd11.*$',
  'samd20': r'^samd20[^b]*$',
  'samd21a': r'^samd21.1[5678].*au?$',
  'samd20b': r'^samd20.*b$',
  'samd21b': r'^samd21.*bu$',
  'samd21c': r'^samd21.1[56].*$',
  'samd21d': r'^samd21.17.*$',
  'samd51a': r'^samd51.*$',
  'samda1': r'^samda1.*a$',
  'samda1b': r'^samda1.*b$',
  'same51': r'^same51.*$',
  'same53': r'^same53.*$',
  'same54': r'^same54.*$',
  'same70a': r'^same70[^b]*$',
  'same70b': r'^same70.*b$',
  'samg51': r'^samg51.*$',
  'samg53': r'^samg53.*$',
  'samg54': r'^samg54.*$',
  'samg55': r'^samg55.*$',
  'samha1a': r'^samha1.*a$',
  'samha1ab': r'^samha1.*b$',
  'saml10': r'^saml10.*$',
  'saml11': r'^saml11.*$',
  'saml21a1': r'^saml21.*a$',
  'saml21b': r'^saml21.*bu?$',
  'saml22': r'^saml22.*$',
  'samr21': r'^samr21.*$',
  'samr30': r'^samr30.*$',
  'samr34': r'^samr34.*$',
  'samr35': r'^samr35.*$',
  'sams70a': r'^sams70[^b]+$',
  'sams70b': r'^sams70.*b$',
  'samv70': r'^samv70[^b]+$',
  'samv70b': r'^samv70.*b$',
  'samv71': r'^samv71[^b]+$',
  'samv71b': r'^samv71.*b$',
}

def get_mcu_family(mcu):
    mcu = mcu.lower()
    for variant_family, match in MCU_FAMILY_SELECTORS.items():
        if re.match(match, mcu):
            return variant_family

    return None

def get_variant_dir(mcu):
    family = get_mcu_family(mcu)
    if family:
        return join(FRAMEWORK_DIR, "variants", PLATFORM_NAME, family)

    sys.stderr.write(
        """Error: There is no variant dir for %s MCU!
        Please add initialization code to your project manually!""" % mcu)
    env.Exit(1)

def adjust_linker_offset(script_name, ldscript):
    offset_address = env.BoardConfig().get("upload.offset_address", "0")
    if int(offset_address, 0)==0:
        return ldscript

    content = ""
    with open(ldscript) as fp:
        content = fp.read()
        # original:     rom      (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00040000
        # transformed:  rom      (rx)  : ORIGIN = 0x00000000+0x2000, LENGTH = 0x00040000-0x2000
        content = re.sub(
            r"^(\s*rom.*ORIGIN[^,]+)(,\s*LENGTH.*)$",
            r"\1+%s\2-%s" % (offset_address, offset_address),
            content, flags=re.MULTILINE)

    offset_script = join(FRAMEWORK_DIR, "platformio", "ldscripts", PLATFORM_NAME,
                    "%s_flash_%s.ld" % (script_name, offset_address))

    with open(offset_script, "w") as fp:
        fp.write(content)

    return offset_script

def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

def get_linker_script(mcu):
    script_name = remove_prefix(mcu.lower(), 'at91')
    ldscript = join(FRAMEWORK_DIR, "platformio", "ldscripts", PLATFORM_NAME,
                    script_name + "_flash.ld")

    if isfile(ldscript):
        return adjust_linker_offset(script_name, ldscript)

    sys.stderr.write(
        """Error: There is no linker script for %s MCU!
        Please add custom linker script to your project manually!""" % mcu)
    env.Exit(1)

env.Append(CPPPATH=[
    join(FRAMEWORK_DIR, "CMSIS", "Core", "Include"),
    join(get_variant_dir(env.BoardConfig().get("build.mcu")), "include")
])

env.Append(LIBPATH=[
    join(FRAMEWORK_DIR, "platformio", "ldscripts", "atmelsam")
])

env.Replace(
    LDSCRIPT_PATH=get_linker_script(env.BoardConfig().get("build.mcu")))

#
# Target: Build Core Library
#

# `BuildSources` because with `BuildLibrary` the vector table doesn't get linked in.
env.BuildSources(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(get_variant_dir(env.BoardConfig().get("build.mcu")), "gcc")
)
