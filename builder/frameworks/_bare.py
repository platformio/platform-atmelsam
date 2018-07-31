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

#
# Default flags for bare-metal programming (without any framework layers)
#

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
board = env.BoardConfig()
build_mcu = env.get("BOARD_MCU", board.get("build.mcu", ""))

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

    LIBS=["m"],
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

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])
