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
from importlib import import_module

from fate_flow.entity.types import ProviderName, ProviderDevice
from fate_flow.runtime.component_provider import ComponentProvider
from fate_flow.runtime.system_settings import DEFAULT_COMPONENTS_WRAPS_MODULE


class FlowHub:
    @staticmethod
    def load_components_wraps(config, module_name=None):
        if not module_name:
            module_name = DEFAULT_COMPONENTS_WRAPS_MODULE  # 默认模块 "fate_flow.hub.components_wraps.fate.FlowWraps"
        class_name = module_name.split(".")[-1]  # 去除掉包路径，剩余类名称
        module = ".".join(module_name.split(".")[:-1])  # 根据“."切片，切片把最后的类名丢掉，剩余包路径的切片，再把切片用“.”连接起来得到原来的包路径
        return getattr(import_module(module), class_name)(config)  # 这里就是实例化 FlowWraps/

    @staticmethod
    def load_provider_entrypoint(provider: ComponentProvider):
        entrypoint = None
        if provider.name == ProviderName.FATE and provider.device == ProviderDevice.LOCAL:
            from fate_flow.hub.provider.local import LocalFateEntrypoint
            entrypoint = LocalFateEntrypoint(provider)
        elif provider.name == ProviderName.FATE_FLOW:
            from fate_flow.hub.provider.local import FATEFLowEntrypoint
            entrypoint = FATEFLowEntrypoint(provider)
        elif provider.device == ProviderDevice.DOCKER:
            from fate_flow.hub.provider.docker import DockerEntrypoint
            entrypoint = DockerEntrypoint(provider)
        return entrypoint

    @staticmethod
    def load_database(engine_name, config, decrypt_key):
        try:
            return getattr(import_module(f"fate_flow.hub.database.{engine_name}"), "get_database_connection")(
                config, decrypt_key)
        except Exception as e:
            try:
                import_module(f"fate_flow.hub.database.{engine_name}")
            except:
                raise SystemError(f"Not support database engine {engine_name}")
            raise SystemError(f"load engine {engine_name} function "
                              f"fate_flow.hub.database.{engine_name}.get_database_connection failed: {e}")
