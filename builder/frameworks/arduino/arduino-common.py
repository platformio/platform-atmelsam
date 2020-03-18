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

import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
build_mcu = env.get("BOARD_MCU", board.get("build.mcu", ""))

MCU_FAMILY = board.get(
    "build.system", "sam" if build_mcu.startswith("at91") else "samd")
assert MCU_FAMILY in ("sam", "samd")

framework_package = "framework-arduino-" + MCU_FAMILY
if board.get("build.core", "").lower() != "arduino":
    framework_package += "-%s" % board.get("build.core").lower()
FRAMEWORK_DIR = platform.get_package_dir(framework_package)

assert os.path.isdir(FRAMEWORK_DIR)

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=gnu11"
    ],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-nostdlib",
        "--param", "max-inline-insns-single=500"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10805),
        ("F_CPU", "$BOARD_F_CPU"),
        "USBCON"
    ],

    CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "cores", "arduino")
    ],

    LIBSOURCE_DIRS=[
        os.path.join(FRAMEWORK_DIR, "libraries")
    ],

    LINKFLAGS=[
        "-Os",
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBS=["m"]
)

variants_dir = os.path.join(
    "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
        "build.variants_dir", "") else os.path.join(FRAMEWORK_DIR, "variants")

if not board.get("build.ldscript", ""):
    env.Append(
        LIBPATH=[
            os.path.join(variants_dir, board.get("build.variant"), "linker_scripts", "gcc")
        ]
    )
    env.Replace(
        LDSCRIPT_PATH=board.get("build.arduino.ldscript", "")
    )

if "build.usb_product" in board:
    env.Append(
        CPPDEFINES=[
            ("USB_VID", board.get("build.hwids")[0][0]),
            ("USB_PID", board.get("build.hwids")[0][1]),
            ("USB_PRODUCT", '\\"%s\\"' %
             board.get("build.usb_product", "").replace('"', "")),
            ("USB_MANUFACTURER", '\\"%s\\"' %
             board.get("vendor", "").replace('"', ""))
        ]
    )
