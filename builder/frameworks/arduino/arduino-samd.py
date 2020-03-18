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

BUILD_CORE = board.get("build.core", "").lower()

framework_package = "framework-arduino-samd"
if BUILD_CORE != "arduino":
    framework_package += "-%s" % BUILD_CORE
FRAMEWORK_DIR = platform.get_package_dir(framework_package)
CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")

assert all(os.path.isdir(d) for d in (FRAMEWORK_DIR, CMSIS_DIR, CMSIS_ATMEL_DIR))

env.SConscript("arduino-common.py")

env.Append(
    CPPPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Include"),
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL")
    ],

    LIBPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
    ],

    LINKFLAGS=[
        "--specs=nosys.specs",
        "--specs=nano.specs"
    ]
)

if board.get("build.cpu") == "cortex-m4":
    env.Prepend(
        CCFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LINKFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LIBS=["arm_cortexM4lf_math"]
    )
else:
    env.Prepend(
        LIBS=["arm_cortexM0l_math"]
    )

if BUILD_CORE == "adafruit":
    env.Append(
        CPPDEFINES=[
            ("USB_CONFIG_POWER", board.get("build.usb_power", 100))
        ],

        CCFLAGS=[
            "-Wno-expansion-to-defined"
        ],

        CPPPATH=[
            os.path.join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB"),
            os.path.join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                 "Adafruit_TinyUSB_ArduinoCore"),
            os.path.join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                 "Adafruit_TinyUSB_ArduinoCore", "tinyusb", "src")
        ]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    variants_dir = os.path.join(
        "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
            "build.variants_dir", "") else os.path.join(FRAMEWORK_DIR, "variants")

    env.Append(
        CPPPATH=[os.path.join(variants_dir, board.get("build.variant"))]
    )
    libs.append(env.BuildLibrary(
        os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"),
        os.path.join(variants_dir, board.get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduino"),
    os.path.join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)
