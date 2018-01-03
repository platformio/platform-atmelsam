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

from os.path import basename, join

from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Builder, Default, DefaultEnvironment)

from platformio.util import get_serialports


def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    env.AutodetectUploadPort()

    upload_options = {}
    if "BOARD" in env:
        upload_options = env.BoardConfig().get("upload", {})

    if not upload_options.get("disable_flushing", False):
        env.FlushSerialBuffer("$UPLOAD_PORT")

    before_ports = get_serialports()

    if upload_options.get("use_1200bps_touch", False):
        env.TouchSerialPort("$UPLOAD_PORT", 1200)

    if upload_options.get("wait_for_upload_port", False):
        env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))

    # use only port name for BOSSA
    if ("/" in env.subst("$UPLOAD_PORT") and
            env.subst("$UPLOAD_PROTOCOL") == "sam-ba"):
        env.Replace(UPLOAD_PORT=basename(env.subst("$UPLOAD_PORT")))


env = DefaultEnvironment()
platform = env.PioPlatform()

env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=gnu11"
    ],

    CCFLAGS=[
        "-g",   # include debugging info (so errors include line numbers)
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mthumb",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
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
        "-mcpu=%s" % env.BoardConfig().get("build.cpu"),
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBS=["c", "gcc", "m"],

    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    PROGSUFFIX=".elf"
)

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        ),
        ElfToHex=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "ihex",
                "-R",
                ".eeprom",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".hex"
        )
    )
)

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

build_mcu = env.get("BOARD_MCU", env.BoardConfig().get("build.mcu", ""))
upload_protocol = env.get("UPLOAD_PROTOCOL",
                          env.BoardConfig().get("upload.protocol", ""))

if ("samd" in build_mcu) or ("samc" in build_mcu):
    env.Append(
        LINKFLAGS=[
            "--specs=nosys.specs",
            "--specs=nano.specs"
        ]
    )

if upload_protocol == "openocd":
    env.Replace(
        UPLOADER="openocd",
        UPLOADERFLAGS=[
            "-s", join(platform.get_package_dir("tool-openocd") or "",
                       "scripts"),
            "-f", join(env.BoardConfig().get("upload.openocdcfg", ""))
        ],

        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS'
    )

    if "zero" in env.subst("$BOARD"):
        env.Append(
            UPLOADERFLAGS=[
                "-s", join(
                    platform.get_package_dir("framework-arduinosam") or "",
                    "variants", env.BoardConfig().get("build.variant"),
                    "openocd_scripts")
            ]
        )

    env.Append(
        UPLOADERFLAGS=[
            "-c", ("telnet_port disabled; program {{$SOURCES}} "
                   "verify reset %s; shutdown" %
                   env.BoardConfig().get("upload.section_start", ""))
        ]
    )

elif upload_protocol == "sam-ba":
    env.Replace(
        UPLOADER="bossac",
        UPLOADERFLAGS=[
            "--port", '"$UPLOAD_PORT"',
            "--erase",
            "--write",
            "--verify",
            "--reset",
            "-U",
            "true" if env.BoardConfig().get(
                "upload.native_usb", False) else "false"
        ],

        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
    )
    if "sam3x8e" in build_mcu:
        env.Append(UPLOADERFLAGS=["--boot"])

    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        env.Prepend(UPLOADERFLAGS=["--info", "--debug"])

elif upload_protocol == "stk500v2":
    env.Replace(
        UPLOADER="avrdude",
        UPLOADERFLAGS=[
            "-p", "atmega2560",  # Arduino M0/Tian upload hook
            "-C", join(
                platform.get_package_dir("tool-avrdude") or "",
                "avrdude.conf"),
            "-c", "$UPLOAD_PROTOCOL",
            "-P", '"$UPLOAD_PORT"',
            "-b", "$UPLOAD_SPEED",
            "-u"
        ],

        UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS -U flash:w:$SOURCES:i'
    )
    if int(ARGUMENTS.get("PIOVERBOSE", 0)):
        env.Prepend(UPLOADERFLAGS=["-v"])

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_firm = join("$BUILD_DIR", "${PROGNAME}.%s" %
                       ("hex" if upload_protocol == "stk500v2" else "bin"))
else:
    target_elf = env.BuildProgram()
    if upload_protocol == "stk500v2":
        target_firm = env.ElfToHex(target_elf)
    else:
        target_firm = env.ElfToBin(target_elf)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

if upload_protocol == "openocd":
    target_upload = env.Alias(
        "upload", target_firm,
        env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE"))
else:
    target_upload = env.Alias(
        "upload", target_firm,
        [env.VerboseAction(BeforeUpload, "Looking for upload port..."),
         env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")])
AlwaysBuild(target_upload)

#
# Setup default targets
#

Default([target_buildprog, target_size])
