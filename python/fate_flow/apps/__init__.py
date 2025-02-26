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
import os.path
import sys
import types
import typing as t

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from flask import Blueprint, Flask, request
from werkzeug.wrappers.request import Request

from fate_flow.controller.permission import PermissionController
from fate_flow.entity.code import ReturnCode
from fate_flow.hook import HookManager
from fate_flow.hook.common.parameters import AuthenticationParameters
from fate_flow.runtime.runtime_config import RuntimeConfig
from fate_flow.runtime.system_settings import API_VERSION, CLIENT_AUTHENTICATION, SITE_AUTHENTICATION, \
    ADMIN_PAGE, PARTY_ID
from fate_flow.utils.api_utils import API
from fate_flow.utils.base_utils import CustomJSONEncoder


__all__ = ['app']

app_list = ["client", "partner", "scheduler", "worker"]

Request.json = property(lambda self: self.get_json(force=True, silent=True))

app = Flask(__name__)
app.url_map.strict_slashes = False
app.errorhandler(422)(API.Output.args_error_response)
app.errorhandler(Exception)(API.Output.server_error_response)
app.json_provider_class = CustomJSONEncoder


def search_pages_path(pages_dir):  # app 文件命名还需要以_app.py结尾才可以
    return [path for path in pages_dir.glob('*_app.py') if not path.name.startswith('.')]


def get_app_module(page_path):
    page_name = page_path.stem.rstrip('app').rstrip("_")
    module_name = '.'.join(page_path.parts[page_path.parts.index('fate_flow')+2:-1] + (page_name, ))
    return module_name


def register_page(page_path, func=None, prefix=API_VERSION):
    page_name = page_path.stem.rstrip('app').rstrip("_")  # 这里是从文件名去掉后面的 _app.py 留下来的
    fate_flow_index = len(page_path.parts) - 1 - page_path.parts[::-1].index("fate_flow")
    module_name = '.'.join(page_path.parts[fate_flow_index:-1] + (page_name, ))
    spec = spec_from_file_location(module_name, page_path)
    page = module_from_spec(spec)
    page.app = app
    page.manager = Blueprint(page_name, module_name)
    rule_methods_list = []

    # rewrite blueprint route to get rule_list
    def route(self, rule: str, **options: t.Any) -> t.Callable:
        def decorator(f: t.Callable) -> t.Callable:
            endpoint = options.pop("endpoint", None)
            rule_methods_list.append((rule, options.get("methods", [])))
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    page.manager.route = types.MethodType(route, page.manager)

    if func:
        page.manager.before_request(func)  # 注册请求拦截器，func为拦截器函数
    sys.modules[module_name] = page
    spec.loader.exec_module(page)
    page_name = getattr(page, 'page_name', page_name)  # 这里是取得*_app.py文件中定义的page_name变量的值
    url_prefix = f'/{prefix}/{page_name}'
    app.register_blueprint(page.manager, url_prefix=url_prefix)  # 注册蓝图
    return page_name, [(os.path.join(url_prefix, rule_methods[0].lstrip("/")), rule_methods[1]) for rule_methods in rule_methods_list]


def client_authentication_before_request():  # client 请求的拦截器
    if CLIENT_AUTHENTICATION:
        result = HookManager.client_authentication(AuthenticationParameters(
            request.path, request.method, request.headers,
            request.form, request.data, request.json, request.full_path
        ))

        if result.code != ReturnCode.Base.SUCCESS:
            return API.Output.json(result.code, result.message)


def site_authentication_before_request():  # site 请求的拦截器（partner/scheduler）
    if SITE_AUTHENTICATION:
        result = HookManager.site_authentication(AuthenticationParameters(
            request.path, request.method, request.headers,
            request.form, request.data, request.json, request.full_path
        ))

        if result.code != ReturnCode.Base.SUCCESS:
            return API.Output.json(result.code, result.message)


def init_apps():
    urls_dict = {}
    before_request_func = {
        "client": client_authentication_before_request,
        "partner": site_authentication_before_request,
        "scheduler": site_authentication_before_request
    }
    for key in app_list:  # ['client', 'partner', 'scheduler', 'worker']
        urls_dict[key] = [register_page(path, before_request_func.get(key)) for path in search_pages_path(Path(__file__).parent / key)]
    # adapter extend apps
    try:
        from fate_flow.adapter import load_adapter_apps
        urls_dict.update(load_adapter_apps(register_page, search_pages_path))  # 这里会注册app的蓝图
    except:
        pass
    if CLIENT_AUTHENTICATION or SITE_AUTHENTICATION:  # 如果开启了鉴权
        _init_permission_group(urls=urls_dict)  # 初始化权限


def _init_permission_group(urls: dict):
    for role, role_items in urls.items():
        super_role = "super_" + role
        if role in ["scheduler", "partner"]:
            role = "site"
            super_role = "site"
        RuntimeConfig.set_client_roles(role, super_role)
        for resource, rule_methods_list in role_items:
            for rule_methods in rule_methods_list:
                rule = rule_methods[0]
                methods = rule_methods[1]
                for method in methods:
                    if resource in ADMIN_PAGE:
                        PermissionController.add_policy(super_role, rule, method)
                    else:
                        PermissionController.add_policy(super_role, rule, method)
                        PermissionController.add_policy(role, rule, method)
        PermissionController.add_role_for_user("admin", super_role, init=True)
    PermissionController.add_role_for_user(PARTY_ID, "site", init=True)


init_apps()  # 这一步把所有的Http api 的route创建出来
