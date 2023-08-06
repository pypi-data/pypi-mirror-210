from pytestifyx import TestCase
from pytestifyx.driver.api import APIRequestMeta
from pytestifyx.utils.requests.requests_config import Config


class APIExample(TestCase, metaclass=APIRequestMeta):
    """
    API测试
    """

    def httpbin_get(self):
        """
        get请求
        应用：httpbin
        接口：https://httpbin.org/get
        :return:
        """

    def httpbin_post(self):
        """
        post请求
        应用：httpbin
        接口：https://httpbin.org/post
        :return:
        """
