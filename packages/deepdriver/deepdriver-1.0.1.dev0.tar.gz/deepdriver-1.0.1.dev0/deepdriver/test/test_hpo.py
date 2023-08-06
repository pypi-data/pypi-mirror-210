import logging
from unittest import TestCase

import deepdriver
from setting import Setting

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestHPO(TestCase):
    _artifact_name = "cat6"
    _artifact_type = "dataset"
    _exp_name = "bokchi_project5"
    

    @classmethod
    def setUpClass(cls):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)  # dev
        login_result = deepdriver.login(key=Setting.LOGIN_KEY)
        run = deepdriver.init(exp_name=TestHPO._exp_name,
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    def test_hpo(self):
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

            return 1

        deepdriver.run_hpo(exp_name=_exp_name, func=func, count=50)

    def test_hpo_config(self):
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
            },
            "env": {
                "gpu_count": 1,
                "cuda_version": "10.1"
            }
        }
        _exp_name = "EXP4"

        deepdriver.create_hpo(exp_name=_exp_name, hpo_config=hpo_configuration)

        def func():
            x = deepdriver.config.values_int
            y = (x - 2) ** 2
            return y

        deepdriver.run_hpo(exp_name=_exp_name, func=func, count=50)

    def test_hpo_prepare(self):
        # create hpo
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
        _exp_name = "EXP3"
        _team_name = "TEAM1"
        deepdriver.create_hpo(exp_name=_exp_name, hpo_config=hpo_configuration)

        # code artifact create
        arti_code = deepdriver.Artifacts(name="TRAIN01", type="CODE")
        arti_code.add("src")
        deepdriver.upload_artifact(arti_code)

        # dataset artifact create
        arti_dataset = deepdriver.Artifacts(name="DATA01", type="DATA")
        arti_dataset.add("cat_dog")
        deepdriver.upload_artifact(arti_dataset)

        artifact = {
            "code":
                {"type": "CODE",
                 "name": "TRAIN01",
                 "file": "main.py",
                 "fun": "train",
                 # "exp_name":"ee",
                 },
            "dataset":
                {
                    "type": "DATA",
                    "name": "DATA01",
                    # "exp_name":"ee",
                }
        }

        result, dataset_path = deepdriver.prepare_dataset(artifact["dataset"])
        self.assertEqual(result, True)

        result, code_path, func = deepdriver.prepare_code(artifact["code"])
        self.assertEqual(result, True)

        # # run HPO
        # deepdriver.run_hpo(exp_name=_exp_name, artifact=artifact)
