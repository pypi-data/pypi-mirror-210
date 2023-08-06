import logging
from unittest import TestCase


from setting import Setting
import deepdriver

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestLog(TestCase):

    _HTTP_HOST = "api.bokchi.com:443"
    _GRPC_HOSt = "grpc.bokchi.com:443"
    # GRPC_HOSt = "20220701-dev-grpc.bokchi.com:443"
    _IS_GRPC_SECURE = True
    _IS_GTTP_SECURE = True
    _LOGIN_KEY = "ZWYyMmI4ODI1ZjE0OTIwODM1MzRlM2YxYTljMzFiZGVkOTdhZjJmODhkOWQ1M2EwY2M1Njg0ZGFiYjdkMTljMg=="

    def make_exp_name():
        import socket
        from datetime import datetime
        host_name = socket.gethostname()
        date = datetime.today().strftime("%Y%m%d")

        return "exp" + "_" + host_name + "_" + date


    @classmethod
    def setUpClass(cl):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


    def test_init_without_certi(self):
        deepdriver.setting(http_host=TestLog._HTTP_HOST, grpc_host=TestLog._GRPC_HOSt,  use_grpc_tls =TestLog._IS_GRPC_SECURE, use_https=TestLog._IS_GTTP_SECURE)
        deepdriver.login(key=TestLog._LOGIN_KEY)
        exp_name =TestLog.make_exp_name()
        print(exp_name)
        run = deepdriver.init(exp_name="test_https_local",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
        deepdriver.log({"a":1 , "b":2})
        deepdriver.finish()

    def test_init_with_certi(self):
        deepdriver.setting(http_host=TestLog._HTTP_HOST, grpc_host=TestLog._GRPC_HOSt,
                           use_grpc_tls=TestLog._IS_GRPC_SECURE, use_https=TestLog._IS_GTTP_SECURE,
                           cert_file="./lgcns.crt")
        deepdriver.login(key=TestLog._LOGIN_KEY)
        exp_name = TestLog.make_exp_name()
        print(exp_name)
        run = deepdriver.init(exp_name="test_https_local",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

        deepdriver.finish()

    def test_init_and_upload_table_log(self):
        deepdriver.setting(http_host=TestLog._HTTP_HOST, grpc_host=TestLog._GRPC_HOSt,
                           use_grpc_tls=TestLog._IS_GRPC_SECURE, use_https=TestLog._IS_GTTP_SECURE)
        deepdriver.login(key=TestLog._LOGIN_KEY)
        exp_name = TestLog.make_exp_name()
        print(exp_name)
        run = deepdriver.init(exp_name="test_https_local",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

        deep_df = deepdriver.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        table = deepdriver.Table(data=deep_df)
        print(table.to_json("table"))
        # table.upload()    # not use
        deepdriver.log({"table": table, "a": "b"})

        deepdriver.finish()

    def test_init_wiht_certi_and_upload_table_log(self):
        deepdriver.setting(http_host=TestLog._HTTP_HOST, grpc_host=TestLog._GRPC_HOSt,
                           use_grpc_tls=TestLog._IS_GRPC_SECURE, use_https=TestLog._IS_GTTP_SECURE, cert_file="./lgcns.crt")
        deepdriver.login(key=TestLog._LOGIN_KEY)
        exp_name = TestLog.make_exp_name()
        print(exp_name)
        run = deepdriver.init(exp_name="test_https_local",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

        deep_df = deepdriver.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        table = deepdriver.Table(data=deep_df)
        print(table.to_json("table"))
        # table.upload()    # not use
        deepdriver.log({"table": table, "a": "b"})

        deepdriver.finish()

