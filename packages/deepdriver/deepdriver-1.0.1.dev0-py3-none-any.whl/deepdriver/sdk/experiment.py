import json
import os
import re
from typing import Dict, Callable, Tuple, Union
from urllib.parse import urljoin

import optuna
import ast
from assertpy import assert_that

from optuna.exceptions import DuplicatedStudyError

import deepdriver
from deepdriver import logger
from deepdriver import util
from deepdriver.sdk.config import Config
from deepdriver.sdk.data_types.experiment import set_experiment, Experiment, get_experiment
from deepdriver.sdk.data_types.run import set_run, Run, get_run
from deepdriver.sdk.interface import interface
from importlib.machinery import SourceFileLoader

@util.login_required
def init(exp_name: str = "", team_name: str = "", run_name: str = "", config: Dict = None) -> Run:
    """ # 실행과 실험환경을 만드는 함수 """
    # exp_name 변수 vailidation
    if exp_name:
        pattern = re.compile('[^a-zA-Z0-9._-]+')
        if pattern.findall(exp_name):
            logger.error("init() failed : exp_name은 숫자(number), 영문자(alphabet), 언더바(_), 온점(.)만 가능합니다.")
            return None

        if len(exp_name) >= 50:
            logger.error("init() failed :  exp_name의 최대 길이는 50자 미만입니다. [max length 50]")
            return None

    rsp = interface.init(exp_name, team_name, run_name, config)
    if 'baseUrl' in rsp and rsp['baseUrl']:
        run_url = urljoin(rsp['baseUrl'], rsp['runUrl'])
    else:
        run_url = urljoin(f"http://{interface.get_http_host_ip()}:9111", rsp['runUrl'])

    run = Run(rsp["teamName"], rsp["expName"], rsp["runName"], rsp["runId"], run_url)
    logger.info("DeepDriver initialized\n"
                f"Team Name={rsp['teamName']}\n"
                f"Exp Name={rsp['expName']}\n"
                f"Run Name={rsp['runName']}\n"
                f"Run URL={run_url}"
                )
    set_run(run)

    # init pytoch Log (delete for lazyload)
    # set_torch_log(TorchLog())

    # init config
    deepdriver.config = Config()
    if config:
        for key, value in config.items():
            setattr(deepdriver.config, key, value)

    return run


@util.login_required
def create_hpo(exp_name: str = "", team_name: str = "", remote: bool = False, hpo_config: Union[str, Dict] = None) -> (bool, int):

    if isinstance(hpo_config, str):
        # str 인 경우 파일을 읽어서 hpo_config json(dict)를 생성
        with open(hpo_config, "rb") as f:
            hpo_config = json.loads(f.read())

    # hpo_config['parameters']를 REST API스펙에 맞게 key-value 형식으로 변환
    if hpo_config and 'parameters' in hpo_config:
        parameters_dict = hpo_config['parameters']
        key_value_parameters_list = []
        for key, value in parameters_dict.items():
            key_value_dict = {
                "key": key,
                # "value": {
                #     next(iter(value.keys())): next(iter(value.values()))
                # }
            }
            if 'range' in value.keys():
                key_value_dict['value'] = {'range': value['range']}
                if 'distribution' in value.keys():
                    key_value_dict['description'] = value['distribution']

            if 'values' in value.keys():
                key_value_dict['value'] = {'values': value['values']}

            key_value_parameters_list.append(key_value_dict)

        hpo_config['parameters'] = key_value_parameters_list

    if hpo_config and 'env' in hpo_config:
        env_dict = hpo_config['env']
        key_value_parameters_list = []
        for key, value in env_dict.items():
            key_value_dict = {
                "key": key,
                "value": value
            }
            key_value_parameters_list.append(key_value_dict)
        hpo_config['env'] = key_value_parameters_list


    rsp = interface.create_hpo(exp_name, team_name, hpo_config)
    logger.info("HPO initialized\n"
                f"Team Name={rsp['teamName']}\n"
                f"Exp Name={rsp['expName']}\n"
                f"Exp Url={rsp['expUrl']}"
                )
    set_experiment(Experiment(exp_name=rsp['expName'], team_name=rsp['teamName']))
    # optuna 최적화 실행
    if not remote:
        def get_optuna_sampler(hpo_config: dict) -> optuna.samplers.BaseSampler:
            type = hpo_config['method']

            if type.lower() == "random":
                return optuna.samplers.RandomSampler()
            elif type.lower() == "grid":
                search_space = {}
                for item in hpo_config['parameters']:
                    key_ = item['key']
                    value_ = list(item['value'].values())[0]
                    search_space[key_] = value_
                logger.debug(f"search_space : {search_space}")
                return optuna.samplers.GridSampler(search_space)
            elif type.lower() == "bayesian":
                return optuna.samplers.TPESampler()

        team_name_ = team_name or get_experiment().team_name  # team 이름이 입력되지 않은경우 run에 설정된 team 이름을 사용
        try:
            optuna.create_study(study_name=team_name_ + "_" + exp_name,
                                storage="postgresql://hpo:hpo@ce-postg.bokchi.com:5432/hpo",  # TODO : 변경예정
                                direction=hpo_config['metric']['goal'],
                                sampler=get_optuna_sampler(hpo_config),
                                )
        except DuplicatedStudyError:
            logger.error("optuna study aleady exist ! \n please create experiment with another name.")
        except Exception:
            logger.info("please check url ")

    return rsp['result'], rsp['expId']


@util.login_required
def run_hpo(exp_name: str = "", team_name: str = "", remote: bool = False, hpo_config: Dict  = None,
            func: Callable = None, count: int = 10, artifact: Union[str, Dict] = None, job_count: int = 0) -> bool:
    # assert_that(func).is_not_none()

    result1, hpoConfig, team_name_from_hpo = get_hpo(exp_name=exp_name, team_name=team_name)
    #logger.info("team_name" +team_name_from_hpo)
    if not result1:
        raise Exception("HPO not found")
    result2, study = load_hpo(exp_name=exp_name, team_name=team_name_from_hpo)

    if isinstance(artifact, str):
        # artifact 가 str인 경우 path로 보고 파일을 읽어서 json(dict)로 만듬
        with open(artifact,  "rb") as f:
            artifact = json.loads(f.read())


    if artifact:
        if not get_run():
            deepdriver.init(team_name=team_name_from_hpo, exp_name=artifact["code"]["exp_name"])
        if "dataset" in artifact:
            result, dataset_path = prepare_dataset(artifact["dataset"])
            if result:
                hpoConfig['dataset_path'] = dataset_path
        if "code" in artifact:
            result, code_path, func = prepare_code(artifact["code"])
            if result:
                hpoConfig['code_path'] = code_path

    result3 = run_optimize(exp_name=exp_name, team_name=team_name_from_hpo, func=func, config=hpoConfig, count=count,
                           study=study)

    return True


@util.login_required
def prepare_dataset(dataset: dict = None) -> Tuple[bool, str]:
    assert_that(dataset).is_not_none()

    arti = deepdriver.get_artifact(**{key:dataset[key] for key in dataset.keys() if key in ['name', 'type', 'tag', 'team_name', 'exp_name']})
    if arti.entry_list == []:
        logger.error(f"artifat(name={dataset['name']}, type={dataset['type']}) have no entries")
        return False, None
    else:
        path = arti.download()
        return True, path


@util.login_required
def prepare_code(code: dict = None) -> Tuple[bool, str, Callable]:
    assert_that(code).is_not_none()

    arti = deepdriver.get_artifact(**{key:code[key] for key in code.keys() if key in ['name', 'type', 'tag', 'team_name', 'exp_name']})
    if arti.entry_list == []:
        return False, None, None
    else:
        path = arti.download()
        # finding code file in entry_list
        file_path = next((entry.local_path for entry in arti.entry_list if entry.path.endswith(code['file'])),
                               None)
        if not file_path:
            raise Exception(f'cannot find file({os.path.join(path, code["file"])}) in artifcat')


        loaded_module = SourceFileLoader(__name__, file_path).load_module()   # dynamically load module(with current module name)
        if code['fun'] not in dir(loaded_module):
            raise Exception(f'cannot find function({code["func"]}) in file([code["file"]])')


        # # dynamically function load from file
        # with open(file_path, "r") as file:
        #     file_content = file.read()
        # node = ast.parse(file_content)
        #
        # looking_for_body = next((body for body in node.body if isinstance(body, ast.FunctionDef) and body.name == code['fun']), None)
        # if not looking_for_body:
        #     raise Exception(f'cannot find function({code["func"]}) in file_entry_list')
        # func_name = looking_for_body.name
        # func_source = ast.get_source_segment(file_content, looking_for_body)
        # exec(func_source)

        return True, path, eval(code['fun'])


@util.login_required
def get_hpo(exp_name: str = "", team_name: str = "") -> (bool, Dict, str):

    rsp = interface.get_hpo(exp_name, team_name)

    if rsp['result'] == "success":
        return True, rsp['hpoConfig'], rsp['teamName']
    else:
        return False, None, None


@util.login_required
def load_hpo(exp_name: str = "", team_name: str = "") -> (bool, optuna.study.study.Study):
    try:
        study = optuna.load_study(study_name=team_name + "_" + exp_name,
                                  storage="postgresql://hpo:hpo@ce-postg.bokchi.com:5432/hpo")
    except Exception as e:
        logger.exception(e)
        return False, None
    return True, study


@util.login_required
def run_optimize(exp_name: str = "", team_name: str = "", func: Callable = None, config: Dict = {},
                 count: int = 10, study: optuna.study.study.Study = None) -> bool:
    def get_wrapped_func(exp_name, team_name, func, config):
        return lambda trial: objective(trial, exp_name, team_name, func, config)

    def objective(trial, exp_name, team_name, func, config):
        deepdriver.init(team_name=team_name, exp_name=exp_name)
        get_config(trial, config)
        y = func()
        deepdriver.log({"result_score": y})
        deepdriver.finish()
        return y

    def get_config(trial, config):
        # config 의 dataset_path, code_path를 config에 저장
        if ("dataset_path" in config) and ("code_path" in config):
            deepdriver.config.dataset_path = config['dataset_path']
            deepdriver.config.code_path = config['code_path']

        # config 의 parameters 내용을 조건에  따라 하기와 같은 코드로 변환
        for item_dict in config['parameters']:
            key: str = item_dict['key']
            sub_key = next(iter(item_dict['value'].keys()))  # 'values' or 'range'
            values: list = next(iter(item_dict['value'].values()))
            suggest = None
            if sub_key == "range":
                if 'description' in item_dict and item_dict['description']:
                    # 'description'(distribution)이 있는 경우
                    if item_dict['description'] == "uniform":
                        suggest = trial.suggest_uniform(item_dict['description'], min(values), max(values))
                    if item_dict['description'] == "log_uniform":
                        suggest = trial.suggest_loguniform(item_dict['description'], min(values), max(values))
                else:
                    if all(isinstance(x, float) for x in values):
                        suggest = trial.suggest_float(key, min(values), max(values))
                    if all(isinstance(x, int) for x in values):
                        suggest = trial.suggest_int(key, min(values), max(values))
                if suggest:
                    exec(f'deepdriver.config.{key} = suggest')
                else:
                    logger.error(f"error : {item_dict}")
            elif sub_key == "values":
                exec(f'deepdriver.config.{key} = trial.suggest_categorical("{key}", {values})')

        logger.debug(f"deepdriver.config. : {deepdriver.config.__dict__}")


    try:
        study = study.optimize(get_wrapped_func(exp_name, team_name, func, config), n_trials=count)
    except Exception as e:
        logger.exception(e)
        return False, None
    return True, study
