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
            upload_protocol = self.board_config(variables.get("board")).get(
                "upload.protocol", "")
            upload_tool = None
            if upload_protocol == "openocd":
                upload_tool = "tool-openocd"
            elif upload_protocol == "sam-ba":
                upload_tool = "tool-bossac"
            elif upload_protocol == "stk500v2":
                upload_tool = "tool-avrdude"

            if upload_tool:
                for name, opts in self.packages.items():
                    if "type" not in opts or opts['type'] != "uploader":
                        continue
                    if name != upload_tool:
                        del self.packages[name]

        return PlatformBase.configure_default_packages(
            self, variables, targets)
