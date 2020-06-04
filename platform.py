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

from platform import system

from platformio.managers.platform import PlatformBase
from platformio.util import get_systype


class AtmelsamPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if not variables.get("board"):
            return PlatformBase.configure_default_packages(
                self, variables, targets)
        board = self.board_config(variables.get("board"))
        upload_protocol = variables.get("upload_protocol",
                                        board.get("upload.protocol", ""))
        disabled_pkgs = []
        upload_tool = "tool-openocd"
        if upload_protocol == "sam-ba":
            upload_tool = "tool-bossac"
        elif upload_protocol == "stk500v2":
            upload_tool = "tool-avrdude"
        elif upload_protocol == "jlink":
            upload_tool = "tool-jlink"
        elif upload_protocol == "mbctool":
            upload_tool = "tool-mbctool"

        if upload_tool:
            for name, opts in self.packages.items():
                if "type" not in opts or opts['type'] != "uploader":
                    continue
                if name != upload_tool:
                    disabled_pkgs.append(name)

        build_core = variables.get(
            "board_build.core", self.board_config(variables.get("board")).get(
                "build.core", "arduino")).lower()

        if "arduino" in variables.get("pioframework", []):
            framework_package = "framework-arduino-%s" % (
                "sam" if board.get("build.mcu", "").startswith("at91") else "samd")

            if build_core != "arduino":
                framework_package += "-" + build_core
            if build_core == "mbcwb":
                self.packages["tool-mbctool"]["type"] = "uploader"
                self.packages["tool-mbctool"]["optional"] = False
                framework_package = "framework-arduino-mbcwb"

            self.frameworks["arduino"]["package"] = framework_package
            if not board.get("build.mcu", "").startswith("samd"):
                self.packages["framework-arduino-sam"]["optional"] = True
            if framework_package in self.packages:
                self.packages[framework_package]["optional"] = False
            self.packages["framework-cmsis"]["optional"] = False
            self.packages["framework-cmsis-atmel"]["optional"] = False
            if build_core in ("sodaq", "tuino0", "reprap"):
                self.packages["framework-cmsis-atmel"]["version"] = "~1.1.0"

        if "mbed" in variables.get("pioframework", []):
            self.packages["toolchain-gccarmnoneeabi"][
                'version'] = ">=1.60301.0,<1.80000.0"
        if "simba" in variables.get("pioframework", []):
            self.packages["toolchain-gccarmnoneeabi"][
                'version'] = ">=1.40803.0,<1.40805.0"
        if (board.get("build.core", "") in ("adafruit", "seeed")
                and "tool-bossac" in self.packages
                and board.get("build.mcu", "").startswith("samd51")):
            self.packages["tool-bossac"]['version'] = "~1.10900.0"
        if "zephyr" in variables.get("pioframework", []):
            for p in self.packages:
                if p.startswith("framework-zephyr-") or p in (
                    "tool-cmake", "tool-dtc", "tool-ninja"):
                    self.packages[p]["optional"] = False
            self.packages['toolchain-gccarmnoneeabi']['version'] = "~1.80201.0"
            if "windows" not in get_systype():
                self.packages['tool-gperf']['optional'] = False

        for name in disabled_pkgs:
            del self.packages[name]
        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug['tools'] = {}

        # Atmel Ice / J-Link / BlackMagic Probe
        tools = ("blackmagic", "jlink", "atmel-ice", "cmsis-dap", "stlink")
        for link in tools:
            if link not in upload_protocols or link in debug['tools']:
                continue
            if link == "blackmagic":
                debug['tools']['blackmagic'] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }

            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if system() == "Windows" else
                                       "JLinkGDBServer")
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }

            else:
                openocd_chipname = debug.get("openocd_chipname")
                assert openocd_chipname
                openocd_cmds = ["set CHIPNAME %s" % openocd_chipname]
                if link == "stlink" and "at91sam3" in openocd_chipname:
                    openocd_cmds.append("set CPUTAPID 0x2ba01477")
                server_args = [
                    "-s", "$PACKAGE_DIR/scripts",
                    "-f", "interface/%s.cfg" % (
                        "cmsis-dap" if link == "atmel-ice" else link),
                    "-c", "; ".join(openocd_cmds),
                    "-f", "target/%s.cfg" % debug.get("openocd_target")
                ]
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }
                if link == "stlink":
                    debug['tools'][link]['load_cmd'] = "preload"

        board.manifest['debug'] = debug
        return board
