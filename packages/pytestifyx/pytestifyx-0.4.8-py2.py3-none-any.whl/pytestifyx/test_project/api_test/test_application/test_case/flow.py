from pytest_cases import parametrize_with_cases

from pytestifyx import TestCase

from ..test_data.busi import BusiAPIData
from .busi import TestBusiAPISample


class TestFlowAPISample(TestCase):
    busi = TestBusiAPISample()

    @parametrize_with_cases('param', cases=BusiAPIData, prefix="busi_")
    def test_flow_api_case(self, param):
        response = self.busi.test_busi_api_case_get(param)
        response = self.busi.test_busi_api_case_post(param)
        assert response.status_code == 200
        return response
