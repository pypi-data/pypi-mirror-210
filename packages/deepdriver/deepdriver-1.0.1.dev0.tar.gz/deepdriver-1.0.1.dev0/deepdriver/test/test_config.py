import logging
from unittest import TestCase

import deepdriver
from deepdriver.sdk.config import Config
from setting import Setting

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
        deepdriver.finish()

    def test_config_basic(self):
        deepdriver.init()
        deepdriver.config.title = "TEST_TITLE"
        deepdriver.config.epochs = 4
        deepdriver.config.test_dict = {"item": "value"}
        self.assertEqual(deepdriver.config.title, "TEST_TITLE")
        self.assertEqual(deepdriver.config.epochs, 4)
        self.assertEqual(deepdriver.config.test_dict, {"item": "value"})

        # after deepdriver.init()
        deepdriver.init(config={"epochs": 10})
        self.assertEqual(deepdriver.config.epochs, 10)
        self.assertEqual(deepdriver.config.keys(), ["epochs"])

    def test_config_method(self):
        deepdriver.init()
        items = [("title", "TEST_TITLE"), ("epochs", 4)]

        deepdriver.config.title = "TEST_TITLE"
        deepdriver.config.epochs = 4
        deepdriver.config.test_dict = {"item": "value"}

        self.assertEqual(deepdriver.config.Items(),
                         [("title", "TEST_TITLE"), ("epochs", 4), ('test_dict', {'item': 'value'})])
        self.assertEqual(deepdriver.config.keys(), ["title", "epochs", "test_dict"])
        self.assertEqual(deepdriver.config.values(), ["TEST_TITLE", 4, {'item': 'value'}])

        self.assertEqual(deepdriver.config.get("title"), "TEST_TITLE")
        self.assertEqual(deepdriver.config.get("not_exists_key"), None)
        self.assertEqual(deepdriver.config.get("test_dict"), {"item": "value"})

    def test_config_update(self):
        deepdriver.init()
        deepdriver.config.batch_size = 64  # 컨피그값  추가
        deepdriver.config.title = "TEST_TITLE"
        deepdriver.config.epochs = 4
        deepdriver.config.test_dict = {"item": "value"}
        result = deepdriver.update()  # config 리스트 전송
        self.assertEqual(result, True)
