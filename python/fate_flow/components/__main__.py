#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
execute with python -m fate.components --config xxx
"""

if __name__ == "__main__":
    import click  # click 是一个命令行工具，可以很方便的实现命令行工具的开发。
    from fate_flow.components.entrypoint.cli import component  # component 是一个命令组

    cli = click.Group()  # Group 是 click 中的一个容器，可以包含多个子命令。
    cli.add_command(component)
    # 这里会调用到 fate_flow/python/fate_flow/components/entrypoint/cli.py 里面的定义的子命令：entrypoint/cleanup/execute
    cli(prog_name="python -m fate_flow.components")
