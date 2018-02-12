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

from platformio.managers.platform import PlatformBase


class AtmelsamPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if variables.get("board"):
            upload_protocol = variables.get("upload_protocol",
                                            self.board_config(
                                                variables.get("board")).get(
                                                    "upload.protocol", ""))
            upload_tool = "tool-openocd"
            if upload_protocol == "sam-ba":
                upload_tool = "tool-bossac"
            elif upload_protocol == "stk500v2":
                upload_tool = "tool-avrdude"

            if upload_tool:
                for name, opts in self.packages.items():
                    if "type" not in opts or opts['type'] != "uploader":
                        continue
                    if name != upload_tool:
                        del self.packages[name]

            if "mbed" in variables.get("pioframework", []):
                self.packages["toolchain-gccarmnoneeabi"][
                    'version'] = ">=1.60301.0"

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
        for link in ("blackmagic", "jlink", "atmel-ice", "cmsis-dap"):
            if link not in upload_protocols or link in debug['tools']:
                continue
            if link == "blackmagic":
                debug['tools']['blackmagic'] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            else:
                openocd_chipname = debug.get("openocd_chipname")
                assert openocd_chipname
                server_args = [
                    "-s", "$PACKAGE_DIR/scripts", "-f",
                    "interface/%s.cfg" % ("cmsis-dap"
                                          if link == "atmel-ice" else link),
                    "-c",
                    "set CHIPNAME %s; set ENDIAN little" % openocd_chipname,
                    "-f",
                    "target/%s.cfg" %
                    ("at91samdXX"
                     if "samd" in openocd_chipname else "at91sam3ax_8x")
                ]
                debug['tools'][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    },
                    "onboard": link in debug.get("onboard_tools", [])
                }

        board.manifest['debug'] = debug
        return board