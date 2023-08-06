import logging
from unittest import TestCase
from setting import Setting
import deepdriver
from deepdriver.sdk.config import Config

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestConfig(TestCase):
    _artifact_name = "cat4"
    _artifact_type = "dataset"
    _exp_name = "bokchi3-project105"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)

    @classmethod
    def tearDownClass(cls):
        pass
        # deepdriver.finish()

    def test_alert_basic(self):
        deepdriver.init()
        result = deepdriver.alert("accuracy > 0.9, early stopping")
        self.assertTrue(result)
