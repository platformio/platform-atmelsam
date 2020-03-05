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

BUILD_CORE = board.get("build.core", "").lower()
FRAMEWORK_DIR = platform.get_package_dir("framework-arduino-samd-mattairtech")

CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = join(FRAMEWORK_DIR, "system", "CMSIS-Atmel")

assert all(isdir(d) for d in (FRAMEWORK_DIR, CMSIS_DIR, CMSIS_ATMEL_DIR))


def process_print_configuration(cpp_defines):
    # if not any(d.startswith("FLOAT_") for d in cpp_defines):
    #     env.Append(CPPDEFINES=["FLOAT_BOTH_DOUBLES_ONLY"])
    pass


def process_timer_configuration(cpp_defines):
    # if not any(d.startswith("TIMER_") for d in cpp_defines):
    #     env.Append(CPPDEFINES=["TIMER_732Hz"])
    pass


def process_clock_configuration(cpp_defines):
    # if not any(d.startswith("CLOCKCONFIG_") for d in cpp_defines):
    #     env.Append(CPPDEFINES=["CLOCKCONFIG_INTERNAL_USB"])
    pass


# USB flags
ARDUINO_USBDEFINES = [("ARDUINO", 10805)]
if "build.usb_product" in board:
    assert board.get("build").get("hwids", [])
    ARDUINO_USBDEFINES += [
        ("USB_VID", board.get("build.hwids")[0][0]),
        ("USB_PID", board.get("build.hwids")[0][1]),
        (
            "USB_PRODUCT",
            '\\"%s\\"' % board.get("build.usb_product", "").replace('"', ""),
        ),
        ("USB_MANUFACTURER", '\\"%s\\"' % board.get("vendor", "").replace('"', "")),
    ]


variants_dir = (
    join("$PROJECT_DIR", board.get("build.variants_dir"))
    if board.get("build.variants_dir", "")
    else join(FRAMEWORK_DIR, "variants")
)

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],
    CFLAGS=["-std=gnu11"],
    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-fsingle-precision-constant",
        "-Wdouble-promotion",
        "-Wall",
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu"),
        "-nostdlib",
        "--param",
        "max-inline-insns-single=500",
    ],
    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++14",
        "-fno-threadsafe-statics",
    ],
    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU"),
        "USBCON",
        "ARM_MATH_CM0PLUS",
        "CONFIG_H_DISABLED",
        "CDC_ONLY",
        "ONE_UART",
        "ONE_WIRE",
        "ONE_SPI",
        "CLOCKCONFIG_INTERNAL_USB",
        "TIMER_732Hz",
        "FLOAT_BOTH_DOUBLES_ONLY",
    ],
    CPPPATH=[
        join(CMSIS_DIR, "CMSIS", "Include"),
        join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL"),
        join(FRAMEWORK_DIR, "cores", "arduino"),
    ],
    LINKFLAGS=[
        "-Os",
        "-mthumb",
        "-mcpu=%s" % board.get("build.cpu"),
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align",
        "--specs=nosys.specs",
        "--specs=nano.specs",
    ],
    LIBPATH=[
        join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
        join(variants_dir, board.get("build.variant")),
    ],
    LIBS=["m"],
)

cpp_defines = env.Flatten(env.get("CPPDEFINES", []))

process_print_configuration(cpp_defines)
process_timer_configuration(cpp_defines)
process_clock_configuration(cpp_defines)

env.Append(ASFLAGS=env.get("CCFLAGS", [])[:], CPPDEFINES=ARDUINO_USBDEFINES)

if not board.get("build.ldscript", ""):
    env.Append(
        LIBPATH=[
            join(
                variants_dir,
                board.get("build.variant"),
                "linker_scripts",
                "gcc",
                board.get("build.arduino.bootloader_dir", ""),
            )
        ]
    )
    env.Replace(LDSCRIPT_PATH=board.get("build.arduino.ldscript", ""))


#
# Lookup for specific core's libraries
#

env.Append(LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")])

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(CPPPATH=[join(variants_dir, board.get("build.variant"))])
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(variants_dir, board.get("build.variant")),
        )
    )

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"), join(FRAMEWORK_DIR, "cores", "arduino")
    )
)


env.Prepend(LIBS=libs)
