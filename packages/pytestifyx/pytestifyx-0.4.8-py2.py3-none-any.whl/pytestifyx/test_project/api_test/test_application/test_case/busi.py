from pytest_cases import parametrize_with_cases

from pytestifyx import TestCase

from ..template.core import APIExample
from ..test_data.busi import BusiAPIData


class TestBusiAPISample(TestCase):
    i = APIExample()

    @parametrize_with_cases('param', cases=BusiAPIData, prefix="busi_")
    def test_busi_api_case_get(self, param, **conf):
        self.ensure_config()
        self.config.set_attr(**conf, concurrent_number=1, request_method='GET')
        response = self.i.httpbin_get(param, self.config)
        assert response.status_code == 200
        return response

    @parametrize_with_cases('param', cases=BusiAPIData, prefix="busi_")
    def test_busi_api_case_post(self, param, **conf):
        self.ensure_config()
        self.config.set_attr(**conf, concurrent_number=1, request_method='POST')
        response = self.i.httpbin_post(param, self.config)
        assert response.status_code == 200
        return response
