import logging
from unittest import TestCase
import deepdriver
from setting import Setting

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestInit(TestCase):
    _artifact_name = "cat4"
    _artifact_type = "dataset"
    _exp_name = "bokchi_project105"
    _login_key = "YjFhN2M0M2Y5MTIxNzI5ZWMyOTQ5OTk5MDUxMjkxYTdmZjBjOTBlODFiMzkxNjdkOTM1ZDU1ZjA2NmUzNDgzNQ=="

    def test_login(self):
        # login fail
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)
        self.assertFalse(login_result)

        # login success
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)
        self.assertTrue(login_result)

    def test_login_id_pw(self):
        # login fail
        # login_result = deepdriver.login(
        #     id=Setting.ID, pw=Setting.PW)
        # self.assertFalse(login_result)

        # login success
        #deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt,  use_grpc_tls =True, use_https=True)
        #deepdriver.login_with()
        login_result = deepdriver.login(
            id=Setting.ID, pw=Setting.PW)
        self.assertTrue(login_result)
        run = deepdriver.init(exp_name="test2",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
        image = deepdriver.Image("./cat_dog/cat/cat.png")
        print(image.to_json("image"))
        deepdriver.log({"image_str": image, "a": "b"})
        deepdriver.finish()

    def test_host_setting(self):
        # http 로 시작하는 REST 주소
        deepdriver.setting(http_host="http://15.164.104.132:9011", grpc_host="15.164.104.132:19051")
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)

    def test_invalid_team_name_init(self):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)
        run = deepdriver.init(exp_name="invalid_team_name+", team_name="test+",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
        self.assertEqual(run, None)
        run = deepdriver.init(exp_name="invalid_team_na@!me", team_name="test-21!",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
        self.assertEqual(run, None)

    def test_hpo(self):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)  # dev
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)

        hpo_configuration = {
            "name": "my-awesome-sweep",
            "metric": {"name": "accuracy", "goal": "maximize"},
            "method": "grid",
            "parameters": {
                # "a": {
                #     "values": [1, 2, 3, 4]
                # },
                "learning_rate": {
                    "distribution": "uniform",
                    "range": [0.01, 0.001],
                }

            }
        }
        _exp_name = "EXP3"
        _team_name = "TEAM1"
        deepdriver.create_hpo(exp_name=_exp_name, hpo_config=hpo_configuration)

        def func():
            x = deepdriver.config.x
            y = (x - 2) ** 2
            return y

        deepdriver.run_hpo(exp_name=_exp_name, func=func, count=50)

    def test_hpo_config(self):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)  # dev
        login_result = deepdriver.login(
            key=Setting.LOGIN_KEY)

        hpo_configuration = {
            "name": "my-awesome-sweep",
            "metric": {"name": "accuracy", "goal": "maximize"},
            "method": "grid",
            "parameters": {
                "range_with_uniform_A": {
                    "distribution": "uniform",
                    "range": [1, 2]
                },
                "range_with_loguniform_A": {
                    "distribution": "log_uniform",
                    "range": [3, 4]
                },
                "range_without_dt_int": {
                    "range": [1, 2]
                },
                "range_without_dt_float": {
                    "range": [1.0, 2.0]
                },
                "values_int": {
                    "values": [1, 2, 3, 4]
                },
                "values_float": {
                    "values": [1.0, 2.0, 3.0, 4.0]
                },
                "values_str": {
                    "values": ["CLASS1", "CLASS2"]
                },
            }
        }
        _exp_name = "EXP4"

        deepdriver.create_hpo(exp_name=_exp_name, hpo_config=hpo_configuration)

        def func():
            x = deepdriver.config.values_int
            y = (x - 2) ** 2
            return y

        deepdriver.run_hpo(exp_name=_exp_name, func=func, count=50)
