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

from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
build_mcu = env.get("BOARD_MCU", board.get("build.mcu", ""))
project_dir = env.get("PROJECT_DIR")

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinosam")
assert isdir(FRAMEWORK_DIR)
BUILD_CORE = board.get("build.core", "")
BUILD_SYSTEM = board.get("build.system", BUILD_CORE)
SYSTEM_DIR = join(FRAMEWORK_DIR, "system", BUILD_SYSTEM)

# USB flags
ARDUINO_USBDEFINES = [("ARDUINO", 10805)]
if "build.usb_product" in env.BoardConfig():
    ARDUINO_USBDEFINES += [
        ("USB_VID", board.get("build.hwids")[0][0]),
        ("USB_PID", board.get("build.hwids")[0][1]),
        ("USB_PRODUCT", '\\"%s\\"' %
         board.get("build.usb_product", "").replace('"', "")),
        ("USB_MANUFACTURER", '\\"%s\\"' %
         board.get("vendor", "").replace('"', ""))
    ]

variant_path = join(FRAMEWORK_DIR, "variants",
                 board.get("build.variant"))
if env.get("OVERRIDE_VARIANT"):
	variant_path = join(project_dir,"variant")
	print('Variant overridden: ' + str(variant_path))

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
        ("F_CPU", "$BOARD_F_CPU"),
        "USBCON"
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", BUILD_CORE)
    ],

    LINKFLAGS=[
        "-Os",
        "-mthumb",
        # "-Wl,--cref", # don't enable it, it prints Cross Reference Table
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBPATH=[
        join(variant_path, "linker_scripts", "gcc")
    ],

    LIBS=["m"]
)

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ],
        LINKFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ]
    )

if ("samd" in build_mcu) or ("samc" in build_mcu):
    env.Append(
        LINKFLAGS=[
            "--specs=nosys.specs",
            "--specs=nano.specs"
        ]
    )

if BUILD_SYSTEM == "samd":
    env.Append(
        CPPPATH=[
            join(SYSTEM_DIR, "CMSIS", "CMSIS", "Include"),
            join(SYSTEM_DIR, "CMSIS-Atmel", "CMSIS", "Device", "ATMEL")
        ],

        LIBPATH=[
            join(SYSTEM_DIR, "CMSIS", "CMSIS", "Lib", "GCC"),
            variant_path
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
            CPPDEFINES=["USE_TINYUSB"],
            CPPPATH=[
                join(FRAMEWORK_DIR, "cores", BUILD_CORE,
                     "Adafruit_TinyUSB_Core"),
                join(FRAMEWORK_DIR, "cores", BUILD_CORE,
                     "Adafruit_TinyUSB_Core", "tinyusb", "src")
            ]
        )

elif BUILD_SYSTEM == "sam":
    env.Append(
        CPPPATH=[
            join(SYSTEM_DIR, "libsam"),
            join(SYSTEM_DIR, "CMSIS", "CMSIS", "Include"),
            join(SYSTEM_DIR, "CMSIS", "Device", "ATMEL")
        ],

        LIBPATH=[
            variant_path
        ],

        LINKFLAGS=[
            "-Wl,--entry=Reset_Handler", "-u", "_sbrk", "-u", "link", "-u",
            "_close", "-u", "_fstat", "-u", "_isatty", "-u", "_lseek", "-u",
            "_read", "-u", "_write", "-u", "_exit", "-u", "kill",
            "-u", "_getpid"
        ],

        LIBS=["sam_sam3x8e_gcc_rel", "gcc"]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],
    CPPDEFINES=ARDUINO_USBDEFINES
)

#
# Lookup for specific core's libraries
#

env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries", "__cores__", BUILD_CORE),
        join(FRAMEWORK_DIR, "libraries")
    ]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[variant_path]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        variant_path
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", BUILD_CORE)
))


env.Prepend(LIBS=libs)
