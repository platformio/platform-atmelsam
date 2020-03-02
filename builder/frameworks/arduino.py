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

from SCons.Script import DefaultEnvironment, SConscript

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
build_mcu = env.get("BOARD_MCU", board.get("build.mcu", ""))

BUILD_CORE = board.get("build.core", "").lower()
MCU_FAMILY = board.get(
    "build.system", "sam" if build_mcu.startswith("at91") else "samd")

if BUILD_CORE == 'mbcwb':
    SConscript(
        join(DefaultEnvironment().PioPlatform().get_package_dir(
            "framework-arduino-mbcwb"), "tools", "platformio-samd-build.py"))
else:
    assert(MCU_FAMILY in ("sam", "samd"))

    FRAMEWORK_DIR = platform.get_package_dir("framework-arduino-%s" % (
        MCU_FAMILY if BUILD_CORE == "arduino" else "%s-%s" % (MCU_FAMILY, BUILD_CORE)))

    if MCU_FAMILY == "samd":
        CMSIS_DIR = platform.get_package_dir("framework-cmsis")
        CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")
        assert isdir(CMSIS_DIR) and isdir(CMSIS_ATMEL_DIR)
    else:
        SYSTEM_DIR = join(FRAMEWORK_DIR, "system")
        assert isdir(SYSTEM_DIR)

    assert isdir(FRAMEWORK_DIR)

    # USB flags
    ARDUINO_USBDEFINES = [("ARDUINO", 10805)]
    if "build.usb_product" in board:
        ARDUINO_USBDEFINES += [
            ("USB_VID", board.get("build.hwids")[0][0]),
            ("USB_PID", board.get("build.hwids")[0][1]),
            ("USB_PRODUCT", '\\"%s\\"' %
             board.get("build.usb_product", "").replace('"', "")),
            ("USB_MANUFACTURER", '\\"%s\\"' %
             board.get("vendor", "").replace('"', ""))
        ]

        if BUILD_CORE == "adafruit":
            ARDUINO_USBDEFINES.append(
                ("USB_CONFIG_POWER", board.get("build.usb_power", 100))
            )


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
            join(FRAMEWORK_DIR, "cores", "arduino")
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

        LIBS=["m"]
    )

    variants_dir = join(
        "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
            "build.variants_dir", "") else join(FRAMEWORK_DIR, "variants")

    if not board.get("build.ldscript", ""):
        env.Append(
            LIBPATH=[
                join(variants_dir, board.get("build.variant"), "linker_scripts", "gcc")
            ])
        env.Replace(LDSCRIPT_PATH=board.get("build.arduino.ldscript", ""))

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

    if MCU_FAMILY == "samd":
        env.Append(
            CPPPATH=[
                join(CMSIS_DIR, "CMSIS", "Include"),
                join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL")
            ],

            LIBPATH=[
                join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
                join(variants_dir, board.get("build.variant"))
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
                CCFLAGS=[
                    "-Wno-expansion-to-defined"
                ],
                CPPPATH=[
                    join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB"),
                    join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                         "Adafruit_TinyUSB_ArduinoCore"),
                    join(FRAMEWORK_DIR, "cores", "arduino", "TinyUSB",
                         "Adafruit_TinyUSB_ArduinoCore", "tinyusb", "src")
                ]
            )

    elif MCU_FAMILY == "sam":
        env.Append(
            CPPPATH=[
                join(SYSTEM_DIR, "libsam"),
                join(SYSTEM_DIR, "CMSIS", "CMSIS", "Include"),
                join(SYSTEM_DIR, "CMSIS", "Device", "ATMEL")
            ],

            LIBPATH=[
                join(variants_dir, board.get("build.variant"))
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
            join(FRAMEWORK_DIR, "libraries")
        ]
    )

    #
    # Target: Build Core Library
    #

    libs = []

    if "build.variant" in board:
        env.Append(
            CPPPATH=[join(variants_dir, board.get("build.variant"))]
        )
        libs.append(env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(variants_dir, board.get("build.variant"))
        ))

    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"),
        join(FRAMEWORK_DIR, "cores", "arduino")
    ))


    env.Prepend(LIBS=libs)
