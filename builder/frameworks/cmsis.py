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

VARIANT_DIRS = {
  'sam3a8c': 'sam3a',
  'sam3xa': 'sam3x',
  'sam3a4c': 'sam3a',
  'sam3n2a': 'sam3n',
  'sam3n4a': 'sam3n',
  'sam3n00a': 'sam3n',
  'sam3n0b': 'sam3n',
  'sam3n0c': 'sam3n',
  'sam3n1b': 'sam3n',
  'sam3n1c': 'sam3n',
  'sam3n00b': 'sam3n',
  'sam3n0a': 'sam3n',
  'sam3n4b': 'sam3n',
  'sam3n4c': 'sam3n',
  'sam3n2b': 'sam3n',
  'sam3n2c': 'sam3n',
  'sam3n1a': 'sam3n',
  'sam3n': 'sam3n',
  'sam3s8c': 'sam3sd8',
  'sam3s8b': 'sam3sd8',
  'sam3sd8c': 'sam3sd8',
  'sam3sd8b': 'sam3sd8',
  'sam3sd8': 'sam3sd8',
  'sam3s1a': 'sam3s',
  'sam3s2b': 'sam3s',
  'sam3s2c': 'sam3s',
  'sam3s': 'sam3s',
  'sam3s4b': 'sam3s',
  'sam3s4c': 'sam3s',
  'sam3s1b': 'sam3s',
  'sam3s1c': 'sam3s',
  'sam3s4a': 'sam3s',
  'sam3s2a': 'sam3s',
  'sam3u': 'sam3u',
  'sam3u1e': 'sam3u',
  'sam3u1c': 'sam3u',
  'sam3u2c': 'sam3u',
  'sam3u4c': 'sam3u',
  'sam3u4e': 'sam3u',
  'sam3u2e': 'sam3u',
  'sam3x8e': 'sam3x',
  'sam3x4c': 'sam3x',
  'sam3x4e': 'sam3x',
  'sam3x8c': 'sam3x',
  'sam3x8h': 'sam3x',
  'sam4cms32c_0': 'sam4cm32',
  'sam4cms32c_1': 'sam4cm32',
  'sam4cmp32c_0': 'sam4cm32',
  'sam4cmp32c_1': 'sam4cm32',
  'sam4cm': 'sam4cm',
  'sam4c8c_1': 'sam4c',
  'sam4c8c_0': 'sam4c',
  'sam4c4c_0': 'sam4c',
  'sam4c4c_1': 'sam4c',
  'sam4c16c_1': 'sam4c',
  'sam4c16c_0': 'sam4c',
  'sam4c': 'sam4c',
  'sam4cmp16c_1': 'sam4cm',
  'sam4cmp16c_0': 'sam4cm',
  'sam4cmp8c_1': 'sam4cm',
  'sam4cmp8c_0': 'sam4cm',
  'sam4cms16c_1': 'sam4cm',
  'sam4cms16c_0': 'sam4cm',
  'sam4cms4c_1': 'sam4cm',
  'sam4cms4c_0': 'sam4cm',
  'sam4cms8c_0': 'sam4cm',
  'sam4cms8c_1': 'sam4cm',
  'sam4cp16b_0': 'sam4cp',
  'sam4cp16b_1': 'sam4cp',
  'sam4cp16c_1': 'sam4cp',
  'sam4cp16c_0': 'sam4cp',
  'sam4cp': 'sam4cp',
  'sam4c32c_0': 'sam4c32',
  'sam4c32c_1': 'sam4c32',
  'sam4c32e_0': 'sam4c32',
  'sam4c32e_1': 'sam4c32',
  'sam4c32': 'sam4c32',
  'sam4e': 'sam4e',
  'sam4e8cb': 'sam4ecb',
  'sam4e16cb': 'sam4ecb',
  'sam4e8e': 'sam4e',
  'sam4e16e': 'sam4e',
  'sam4e16c': 'sam4e',
  'sam4e8c': 'sam4e',
  'sam4ls4c': 'sam4l4',
  'sam4ls4b': 'sam4l4',
  'sam4ls2c': 'sam4l4',
  'sam4ls2b': 'sam4l4',
  'sam4lc4a': 'sam4l4',
  'sam4lc2a': 'sam4l4',
  'sam4ls2a': 'sam4l4',
  'sam4ls4a': 'sam4l4',
  'sam4lc2c': 'sam4l4',
  'sam4lc2b': 'sam4l4',
  'sam4lc4c': 'sam4l4',
  'sam4lc4b': 'sam4l4',
  'sam4lc8a': 'sam4l8',
  'sam4ls8b': 'sam4l8',
  'sam4ls8c': 'sam4l8',
  'sam4lc8b': 'sam4l8',
  'sam4lc8c': 'sam4l8',
  'sam4ls8a': 'sam4l8',
  'sam4n16c': 'sam4n',
  'sam4n16b': 'sam4n',
  'sam4n8b': 'sam4n',
  'sam4n8c': 'sam4n',
  'sam4n': 'sam4n',
  'sam4n8a': 'sam4n',
  'sam4sp': 'sam4sp',
  'sam4sp32a': 'sam4sp',
  'sam4s': 'sam4s',
  'sam4sd16b': 'sam4s',
  'sam4sd16c': 'sam4s',
  'sam4s2a': 'sam4s',
  'sam4sa16b': 'sam4s',
  'sam4sa16c': 'sam4s',
  'sam4s4a': 'sam4s',
  'sam4s4c': 'sam4s',
  'sam4s4b': 'sam4s',
  'sam4s2c': 'sam4s',
  'sam4s2b': 'sam4s',
  'sam4s16b': 'sam4s',
  'sam4s16c': 'sam4s',
  'sam4s8b': 'sam4s',
  'sam4s8c': 'sam4s',
  'sam4sd32c': 'sam4s',
  'sam4sd32b': 'sam4s',
  'samb11': 'samb11',
  'samc20e18a': 'samc20',
  'samc20e15a': 'samc20',
  'samc20g16a': 'samc20',
  'samc20j17au': 'samc20',
  'samc20j15a': 'samc20',
  'samc20j18a': 'samc20',
  'samc20g17a': 'samc20',
  'samc20j18au': 'samc20',
  'samc20j16a': 'samc20',
  'samc20e17a': 'samc20',
  'samc20j17a': 'samc20',
  'samc20g18a': 'samc20',
  'samc20g15a': 'samc20',
  'samc20e16a': 'samc20',
  'samc20n17a': 'samc20n',
  'samc20n18a': 'samc20n',
  'samc21n17a': 'samc21n',
  'samc21n18a': 'samc21n',
  'samc21e18a': 'samc21',
  'samc21g16a': 'samc21',
  'samc21e15a': 'samc21',
  'samc21j15a': 'samc21',
  'samc21j18a': 'samc21',
  'samc21g17a': 'samc21',
  'samc21j18au': 'samc21',
  'samc21j16a': 'samc21',
  'samc21e17a': 'samc21',
  'samc21j17au': 'samc21',
  'samc21j17a': 'samc21',
  'samc21g18a': 'samc21',
  'samc21e16a': 'samc21',
  'samc21g15a': 'samc21',
  'samd09c13a': 'samd09',
  'samd09d14a': 'samd09',
  'samd10d13as': 'samd10',
  'samd10d14au': 'samd10',
  'samd10d13am': 'samd10',
  'samd10c14a': 'samd10',
  'samd10d14am': 'samd10',
  'samd10c13a': 'samd10',
  'samd10d14as': 'samd10',
  'samd11c14a': 'samd11',
  'samd11d14as': 'samd11',
  'samd11d14am': 'samd11',
  'samd11d14au': 'samd11',
  'samd20g17': 'samd20',
  'samd20g16': 'samd20',
  'samd20j17': 'samd20',
  'samd20j16': 'samd20',
  'samd20e16': 'samd20',
  'samd20e17': 'samd20',
  'samd20g17u': 'samd20',
  'samd20e18': 'samd20',
  'samd20j14': 'samd20',
  'samd20j15': 'samd20',
  'samd20g14': 'samd20',
  'samd20g15': 'samd20',
  'samd20g18': 'samd20',
  'samd20j18': 'samd20',
  'samd20g18u': 'samd20',
  'samd20e15': 'samd20',
  'samd20e14': 'samd20',
  'samd20j16b': 'samd20b',
  'samd20g14b': 'samd20b',
  'samd20g15b': 'samd20b',
  'samd20e16b': 'samd20b',
  'samd20j14b': 'samd20b',
  'samd20e15b': 'samd20b',
  'samd20g16b': 'samd20b',
  'samd20j15b': 'samd20b',
  'samd20e14b': 'samd20b',
  'samd21e16bu': 'samd21b',
  'samd21e15bu': 'samd21b',
  'samd21g17l': 'samd21d',
  'samd21j17d': 'samd21d',
  'samd21e17d': 'samd21d',
  'samd21e17du': 'samd21d',
  'samd21g17d': 'samd21d',
  'samd21e17l': 'samd21d',
  'samd21j16b': 'samd21c',
  'samd21g16l': 'samd21c',
  'samd21e16b': 'samd21c',
  'samd21g15b': 'samd21c',
  'samd21e16cu': 'samd21c',
  'samd21e15l': 'samd21c',
  'samd21g16b': 'samd21c',
  'samd21e16l': 'samd21c',
  'samd21g15l': 'samd21c',
  'samd21e15b': 'samd21c',
  'samd21e15cu': 'samd21c',
  'samd21j15b': 'samd21c',
  'samd21g16a': 'samd21a',
  'samd21e15a': 'samd21a',
  'samd21e18a': 'samd21a',
  'samd21j18a': 'samd21a',
  'samd21g17a': 'samd21a',
  'samd21j15a': 'samd21a',
  'samd21g17au': 'samd21a',
  'samd21e17a': 'samd21a',
  'samd21j16a': 'samd21a',
  'samd21g18au': 'samd21a',
  'samd21e16a': 'samd21a',
  'samd21g15a': 'samd21a',
  'samd21j17a': 'samd21a',
  'samd21g18a': 'samd21a',
  'samd51j19a': 'samd51a',
  'samd51p19a': 'samd51a',
  'samd51j20a': 'samd51a',
  'samd51j18a': 'samd51a',
  'samd51p20a': 'samd51a',
  'samd51g19a': 'samd51a',
  'samd51n19a': 'samd51a',
  'samd51g18a': 'samd51a',
  'samd51n20a': 'samd51a',
  'samda1j14b': 'samda1b',
  'samda1e15b': 'samda1b',
  'samda1g16b': 'samda1b',
  'samda1j15b': 'samda1b',
  'samda1e14b': 'samda1b',
  'samda1j16b': 'samda1b',
  'samda1g14b': 'samda1b',
  'samda1g15b': 'samda1b',
  'samda1e16b': 'samda1b',
  'samda1g14a': 'samda1',
  'samda1j16a': 'samda1',
  'samda1g15a': 'samda1',
  'samda1e16a': 'samda1',
  'samda1e15a': 'samda1',
  'samda1g16a': 'samda1',
  'samda1j14a': 'samda1',
  'samda1e14a': 'samda1',
  'samda1j15a': 'samda1',
  'same51j19a': 'same51',
  'same51j18a': 'same51',
  'same51j20a': 'same51',
  'same51n19a': 'same51',
  'same51n20a': 'same51',
  'same53n20a': 'same53',
  'same53n19a': 'same53',
  'same53j18a': 'same53',
  'same53j20a': 'same53',
  'same53j19a': 'same53',
  'same54n20a': 'same54',
  'same54n19a': 'same54',
  'same54p20a': 'same54',
  'same54p19a': 'same54',
  'same70j20b': 'same70b',
  'same70j19b': 'same70b',
  'same70j21b': 'same70b',
  'same70n20b': 'same70b',
  'same70q20b': 'same70b',
  'same70q19b': 'same70b',
  'same70n19b': 'same70b',
  'same70n21b': 'same70b',
  'same70q21b': 'same70b',
  'same70n21': 'same70a',
  'same70n20': 'same70a',
  'same70n19': 'same70a',
  'same70q20': 'same70a',
  'same70q21': 'same70a',
  'same70j20': 'same70a',
  'same70j21': 'same70a',
  'same70j19': 'same70a',
  'same70q19': 'same70a',
  'samg51g18': 'samg51',
  'samg51n18': 'samg51',
  'samg55g19': 'samg55',
  'samg55j19': 'samg55',
  'samg53n19': 'samg53',
  'samg53g19': 'samg53',
  'samg54j19': 'samg54',
  'samg54g19': 'samg54',
  'samg54n19': 'samg54',
  'samha1g15a': 'samha1a',
  'samha1g14a': 'samha1a',
  'samha1g16a': 'samha1a',
  'samha1e16ab': 'samha1ab',
  'samha1g15ab': 'samha1ab',
  'samha1e14ab': 'samha1ab',
  'samha1g14ab': 'samha1ab',
  'samha1g16ab': 'samha1ab',
  'samha1e15ab': 'samha1ab',
  'saml10e15a': 'saml10',
  'saml10d16a': 'saml10',
  'saml10e14a': 'saml10',
  'saml10d15a': 'saml10',
  'saml10d14a': 'saml10',
  'saml10e16a': 'saml10',
  'saml11e15a': 'saml11',
  'saml11e14a': 'saml11',
  'saml11d16a': 'saml11',
  'saml11d15a': 'saml11',
  'saml11e16a': 'saml11',
  'saml11d14a': 'saml11',
  'saml21e18a': 'saml21a1',
  'saml21j18a': 'saml21a1',
  'saml21g18a': 'saml21a1',
  'saml21j16b': 'saml21b',
  'saml21j17bu': 'saml21b',
  'saml21e17b': 'saml21b',
  'saml21g18b': 'saml21b',
  'saml21j17b': 'saml21b',
  'saml21e16b': 'saml21b',
  'saml21j18bu': 'saml21b',
  'saml21e18b': 'saml21b',
  'saml21e15b': 'saml21b',
  'saml21g16b': 'saml21b',
  'saml21g17b': 'saml21b',
  'saml21j18b': 'saml21b',
  'saml22n18a': 'saml22',
  'saml22j17a': 'saml22',
  'saml22g18a': 'saml22',
  'saml22j16a': 'saml22',
  'saml22j18a': 'saml22',
  'saml22g17a': 'saml22',
  'saml22n17a': 'saml22',
  'saml22g16a': 'saml22',
  'saml22n16a': 'saml22',
  'samr21e17a': 'samr21',
  'samr21e16a': 'samr21',
  'samr21g18a': 'samr21',
  'samr21g16a': 'samr21',
  'samr21e18a': 'samr21',
  'samr21g17a': 'samr21',
  'samr21e19a': 'samr21',
  'samr30e18a': 'samr30',
  'samr30g18a': 'samr30',
  'samr34j18b': 'samr34',
  'samr34j16b': 'samr34',
  'samr34j17b': 'samr34',
  'samr35j18b': 'samr35',
  'samr35j16b': 'samr35',
  'samr35j17b': 'samr35',
  'sams70n20b': 'sams70b',
  'sams70q20b': 'sams70b',
  'sams70q19b': 'sams70b',
  'sams70n19b': 'sams70b',
  'sams70n21b': 'sams70b',
  'sams70q21b': 'sams70b',
  'sams70j20b': 'sams70b',
  'sams70j19b': 'sams70b',
  'sams70j21b': 'sams70b',
  'sams70n21': 'sams70a',
  'sams70n20': 'sams70a',
  'sams70n19': 'sams70a',
  'sams70j20': 'sams70a',
  'sams70j21': 'sams70a',
  'sams70q20': 'sams70a',
  'sams70q21': 'sams70a',
  'sams70q19': 'sams70a',
  'sams70j19': 'sams70a',
  'samv70q19b': 'samv70b',
  'samv70n19b': 'samv70b',
  'samv70n20b': 'samv70b',
  'samv70q20b': 'samv70b',
  'samv70j19b': 'samv70b',
  'samv70j20b': 'samv70b',
  'samv70j19': 'samv70',
  'samv70q19': 'samv70',
  'samv70q20': 'samv70',
  'samv70j20': 'samv70',
  'samv70n19': 'samv70',
  'samv70n20': 'samv70',
  'samv71n19': 'samv71',
  'samv71n20': 'samv71',
  'samv71n21': 'samv71',
  'samv71q19': 'samv71',
  'samv71j19': 'samv71',
  'samv71j21': 'samv71',
  'samv71j20': 'samv71',
  'samv71q21': 'samv71',
  'samv71q20': 'samv71',
  'samv71n19b': 'samv71b',
  'samv71q19b': 'samv71b',
  'samv71q21b': 'samv71b',
  'samv71n21b': 'samv71b',
  'samv71q20b': 'samv71b',
  'samv71n20b': 'samv71b',
  'samv71j19b': 'samv71b',
  'samv71j21b': 'samv71b',
  'samv71j20b': 'samv71b',
}

def get_variant_dir(mcu):
    mcu = mcu.lower()
    if mcu not in VARIANT_DIRS:
        sys.stderr.write(
            """Error: There is no variant dir for %s MCU!
            Please add initialization code to your project manually!""" % mcu)
        env.Exit(1)

    return join(FRAMEWORK_DIR, "variants", PLATFORM_NAME, VARIANT_DIRS[mcu])

def adjust_linker_offset(mcu, ldscript):
    offset_address = env.BoardConfig().get("upload.offset_address", None)
    if offset_address is None or int(offset_address, 0)==0:
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

    # offset_script = join("$BUILD_DIR", basename(ldscript))
    offset_script = join(FRAMEWORK_DIR, "platformio", "ldscripts", PLATFORM_NAME,
                    "%s_flash_%s.ld" % (mcu, offset_address))

    with open(offset_script, "w") as fp:
        fp.write(content)

    return offset_script

def get_linker_script(mcu):
    ldscript = join(FRAMEWORK_DIR, "platformio", "ldscripts", PLATFORM_NAME,
                    mcu.lower() + "_flash.ld")

    if isfile(ldscript):
        return adjust_linker_offset(mcu, ldscript)

    sys.stderr.write(
        """Error: There is no linker script for %s MCU!
        Please add custom linker script to your project manually!""" % mcu)
    env.Exit(1)

env.Append(CPPPATH=[
    join(FRAMEWORK_DIR, "CMSIS", "Core", "Include"),
    join(get_variant_dir(env.BoardConfig().get("build.mcu")), "include")
])


env.Replace(
    LDSCRIPT_PATH=get_linker_script(env.BoardConfig().get("build.mcu")))

#
# Target: Build Core Library
#

# Sources because as Library the vector table doesn't get linked in.
env.BuildSources(
    join("$BUILD_DIR", "FrameworkCMSISVariant"),
    join(get_variant_dir(env.BoardConfig().get("build.mcu")), "gcc")
)
