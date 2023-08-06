import importlib
import json

from requests_toolbelt import MultipartEncoder
import requests
from typing import Dict

from pytestifyx.utils.json.core import json_update
from pytestifyx.utils.logs.core import log
from pytestifyx.utils.requests.reload_all import reload_all
from pytestifyx.utils.requests.requests_config import Config

import inspect
import functools


class APIRequestMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                setattr(new_cls, attr_name, cls.generate_api_method(attr_name, attr_value))
        return new_cls

    @staticmethod
    def generate_api_method(name, func):
        @functools.wraps(func)
        def wrapped_func(self, param=None, config: Config = Config(), **kwargs):
            if param is None:
                param = {}
            method_doc = inspect.getdoc(func)
            notes = method_doc.split('\n')[0].strip() if method_doc else "Unknown request"
            log.info(f'--------------{notes}-----------------')
            api_class_file = inspect.getmodule(self).__file__

            response = self.api(api_class_file, name, param, config, **kwargs)
            return response

        return wrapped_func


class BaseRequest:

    @staticmethod
    def get(url, params=None, **kwargs):
        return requests.get(url, params=params, **kwargs)

    @staticmethod
    def post(url, data=None, **kwargs):
        return requests.post(url, data=data, **kwargs)

    @staticmethod
    def put(url, data=None, **kwargs):
        return requests.put(url, data=data, **kwargs)

    @staticmethod
    def delete(url, **kwargs):
        return requests.delete(url, **kwargs)

    def base(self, path, func_name, params, config: Config, **kwargs):
        """
        :param config: 配置参数
        :param path: 模块路径
        :param func_name: 模块方法名
        :param kwargs: 参数
        :param params: 参数
        :return: 响应
        """
        template_body, template_headers, template_url = self.base_init_module(path)

        if 'delete_key' in params:
            config.delete_key = params['delete_key']

        # 解析模版参数
        url, headers, data = self.base_init_prepare_request(config, template_body, template_headers, template_url,
                                                            func_name)

        # 创建 HookedRequest 实例，所有钩子类将自动注册
        generate_parameters_hook_params = {"params": params, "headers": headers, "data": data}
        send_requests_hook_params = {"headers": headers, "url": url, "data": data}
        hooks_params = [
            (GenerateParametersHook, generate_parameters_hook_params, 0),
            (SendRequestHook, send_requests_hook_params, 0),
        ]
        hooked_request = HookedRequest(config, hooks_params)
        results = hooked_request.execute_hooks()
        # 处理钩子函数返回值
        all_hooks_results = {}
        for hook_name, result in results.items():
            # print(f"Result from {hook_name}: {result}")
            all_hooks_results[hook_name] = result
        # print(f"All hooks results: {all_hooks_results}")
        # print(f"Final request params: {all_hooks_results['SendRequestHook'].response}")
        return all_hooks_results['SendRequestHook'].response
        # 处理请求
        # return self.base_request(config, url, headers, data, data_encrypt, params, func_name, **kwargs)

    def base_init_module(self, path):
        """
        初始化导入模块
        :param path: 模块路径
        :return:
        """
        # print(path)
        import_path = path.split('api_test')[1].split('core.py')[0]  # 首尾切割一次
        template_body = self.import_template(import_path, 'body')  # 导入body模块
        template_headers = self.import_template(import_path, 'headers')  # 导入header模块
        template_url = self.import_template(import_path, 'url')  # 导入url模块
        return template_body, template_headers, template_url

    def base_init_prepare_request(self, config, template_body, template_headers, template_url, func_name):
        """
        解析模版参数
        :param config: 配置参数
        :param template_url: url模版
        :param template_headers: header模版
        :param template_body: body模版
        :param func_name: 模块方法名
        :return: url, headers, data
        """
        url = self.get_template_url_prefix_value(template_url, func_name,
                                                 config.env_name) + self.get_template_path_value(template_url,
                                                                                                 func_name,
                                                                                                 config.env_name)  # 获取url模版参数
        headers = self.get_template_value(template_headers, func_name)  # 获取header模版参数
        data = self.get_template_value(template_body, func_name)  # 获取body模版参数
        return url, headers, data

    @staticmethod
    def import_template(path, module_name):
        """
        导入模版
        :param path:  模版路径
        :param module_name:  模块名称
        :return: 模版
        """
        import_module_body = path.replace('\\', '.').replace('/', '.') + module_name  # 兼容路径/和\ 两种分隔符
        template_body = importlib.import_module(import_module_body, 'api_test')  # 导入模块
        return template_body

    @staticmethod
    def reload_template(reload_config, module):
        """
        重新加载模版
        :param reload_config:  是否重新加载的配置
        :param module:  模块名称
        :return:
        """
        if reload_config:
            reload_all(module)

    @staticmethod
    def get_template_value(template, func_name):
        """
        获取模版值
        :param template:  模版
        :param func_name:  模版方法名称
        :return: 模版方法值
        """
        if func_name.startswith('test_'):  # 兼容pytest/unittest写法
            func_name = func_name.replace('test_', '')
        if func_name.endswith('_body_rsa'):  # 先处理rsa加密字段为空的情况
            if hasattr(template, func_name):  # 有_body_rsa则为_body_rsa模块
                return template.__getattribute__(func_name)
            else:  # 没有_body_rsa则返回空字典
                return {}
        try:
            if hasattr(template, 'url_prefix'):  # 有url_prefix则为path模块
                url = template.url_prefix + template.__getattribute__(func_name + '_path')
                return url
            elif hasattr(template, func_name + '_body'):  # 有_body则为_body模块
                return template.__getattribute__(func_name + '_body')
            elif hasattr(template, func_name + '_headers'):  # 特配headers则为特配headers模块
                return template.__getattribute__(func_name + '_headers')
            elif hasattr(template, 'headers'):  # 有headers则为headers模块
                return template.__getattribute__('headers')
        except AttributeError:
            log.error(f'请配置{func_name}模版参数')

    @staticmethod
    def get_template_url_prefix_value(template, func_name, env_name):
        """
        获取模版值
        :param template:  模版
        :param func_name:  模版方法名称
        :param env_name:  环境名称
        :return: 模版方法值
        """
        if func_name.startswith('test_'):  # 兼容pytest/unittest写法
            func_name = func_name.replace('test_', '')
        if hasattr(template, 'url_prefix' + f'_{env_name}'):  # 有url_prefix则为path模块
            url_prefix = template.__getattribute__('url_prefix' + f'_{env_name}')
        elif hasattr(template, func_name + '_url_prefix'):  # 特配headers则为特配headers模块
            url_prefix = template.__getattribute__(func_name + '_url_prefix')
        elif hasattr(template, 'url_prefix'):
            url_prefix = template.url_prefix
        else:
            url_prefix = ''
            log.error(f'请配置{func_name}的url_prefix模板参数')
        return url_prefix

    @staticmethod
    def get_template_path_value(template, func_name, env_name):
        """
        获取模版值
        :param template:  模版
        :param func_name:  模版方法名称
        :param env_name:  环境名称
        :return: 模版方法值
        """
        if func_name.startswith('test_'):  # 兼容pytest/unittest写法
            func_name = func_name.replace('test_', '')
        if hasattr(template, func_name + '_path' + f'_{env_name}'):  # 有url_prefix则为path模块
            path = template.__getattribute__(func_name + '_path' + f'_{env_name}')
        elif hasattr(template, func_name + '_path'):
            path = template.__getattribute__(func_name + '_path')
        else:
            path = ''
            log.error(f'请配置{func_name}的path模板参数')
        return path


class HookMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls.is_hook = True
        return new_cls


def create_hook_instance(config, hook_cls, params, hook_instances):
    hook_cls_name = hook_cls.__name__
    if hook_cls_name not in hook_instances:
        # print(f"Creating hook instance: {hook_cls_name}({params})")
        hook_instances[hook_cls_name] = hook_cls(config, **params)
    return hook_instances[hook_cls_name]


class HookWrapper:
    def __init__(self, config, hook_cls, params, priority=0):
        self.config = config
        self.hook_cls = hook_cls
        self.params = params
        self.priority = priority

    def __call__(self, hook_instances):
        hook_instance = create_hook_instance(self.config, self.hook_cls, self.params, hook_instances)
        hook_instances[self.hook_cls.__name__] = hook_instance
        return hook_instance


class Hook(metaclass=HookMeta):
    def __init__(self, config, priority=0):
        self.config = config
        self.priority = priority

    def should_execute(self):
        raise NotImplementedError()

    def execute(self, **kwargs):
        raise NotImplementedError()


class HookedRequest:
    def __init__(self, config, hooks_params):
        self.config = config
        self.hook_instances = {}  # 将原来的列表类型修改为字典类型
        for hook_cls, params, priority in hooks_params:
            HookWrapper(config, hook_cls, params, priority=priority)(self.hook_instances)

        # 根据优先级从高到低排序钩子实例列表
        self.hook_instances = dict(sorted(self.hook_instances.items(), key=lambda x: x[1].priority))

    def execute_hooks(self, **kwargs) -> Dict[str, any]:
        results = {}
        for hook_name, hook_instance in self.hook_instances.items():
            if hook_instance.should_execute():
                result = hook_instance.execute(**kwargs)
                results[hook_name] = result
        return results


class GenerateParametersHook(Hook):
    def __init__(self, config, params, headers, data, priority=0):
        super().__init__(config, priority)
        self.params = params
        self.headers = headers
        self.data = data

    def should_execute(self):
        return True

    def execute(self):
        """
        生成参数
        :param params:  模版参数
        :param config:  配置参数
        :param data:  请求体
        :return:  请求头，请求体
        """
        # 处理删除的key
        for key in self.config.delete_key:
            if key in self.data:
                self.data.pop(key)

        # 入参替换模版参数
        json_update(self.data, self.params)

        # 特殊处理请求头
        if '_headers' in self.params:
            self.headers.update(self.params['_headers'])

        # 处理请求头同名字段覆盖问题
        if self.config.is_cover_header:
            json_update(self.headers, self.data)  # 入参同名字段替换请求头

        # 处理请求头中的租户id
        if self.config.tenant_id:
            self.headers['tenant-id'] = self.config.tenant_id

        log.info('请求头' + json.dumps(self.headers, indent=4, ensure_ascii=False))

        if self.config.is_request_log:
            if self.config.is_request_log_json_dumps:
                log.info('请求原始报文' + json.dumps(self.data, indent=4, ensure_ascii=False))
            else:
                log.info('请求原始报文' + self.data)

        class Parameters:
            def __init__(self, headers, data):
                self.headers = headers
                self.data = data

        self.config.GenerateParametersHook = Parameters(self.headers, self.data)
        return Parameters(self.headers, self.data)


class SendRequestHook(Hook):
    def __init__(self, config, headers, url, data, priority=0):
        super().__init__(config, priority)
        self.headers = headers
        self.url = url
        self.data = data

    def should_execute(self):
        return True

    def execute(self):
        # res = self.config.GenerateParametersHook
        # print(res.headers)
        log.info(f'----------------请求头为{self.headers}---------------')
        log.info(f'----------------请求地址为{self.url}---------------')
        if self.config.request_method.upper() == 'GET':
            log.info('----------------请求方式为GET---------------')
            response = requests.get(headers=self.headers, url=self.url, params=self.data, timeout=2000)
        elif self.config.request_method.upper() == 'POST':
            log.info('----------------请求方式为POST---------------')
            if self.config.content_type.upper() == 'JSON':
                self.headers['Content-Type'] = 'application/json'
                response = requests.post(headers=self.headers, url=self.url,data=json.dumps(self.data) if self.config.is_json_dumps else self.data,timeout=2000)
            elif self.config.content_type == 'multipart/form-data':  # 处理文件上传
                m = MultipartEncoder(fields=self.data)
                self.headers['Content-Type'] = m.content_type
                response = requests.post(headers=self.headers, url=self.url, data=m, timeout=2000)
            else:
                raise Exception('暂不支持的请求方式')

        log.info('接口的响应时间为：' + str(response.elapsed.total_seconds()))
        if self.config.is_response_log:
            log.info(response.text)
            log.info(response.headers)

        class Parameters:
            def __init__(self, response):
                self.response = response

        return Parameters(response)
