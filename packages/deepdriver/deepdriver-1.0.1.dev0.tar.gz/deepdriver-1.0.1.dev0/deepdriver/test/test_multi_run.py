import logging
from unittest import TestCase

import PIL
from setting import Setting
import deepdriver

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
run1 = None
run2 = None


class TestMultipleLog(TestCase):
    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)
        global run1
        run1 = deepdriver.init(exp_name="my-bokchi-multi-test",
                               config={'epoch': 5, 'batch_size': 32, 'hidden_layer': 64})

        global run2
        run2 = deepdriver.init(exp_name="my-bokchi-multi-test2",
                               config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    @classmethod
    def tearDownClass(cls):
        run1.finish()
        run2.finish()

    def test_multi_log(self):
        for i in range(10):
            run1.log({"log_num": "run1" + str(i)})
            run2.log({"log_num": "run2" + str(i)})
    # def test_multil_artifact(self):
