import json
import logging
import requests
from  urllib.parse import ParseResult
from typing import Dict, List, Tuple, TYPE_CHECKING, Union
import urllib3
from deepdriver.sdk import util
from deepdriver import logger
import deepdriver.version as version
from deepdriver.sdk.data_types.artifactInfo import ArtifactInfo
from deepdriver.sdk.data_types.uploadInfo import UploadInfo
from deepdriver.sdk.interface.file_upload import Progress
from deepdriver.sdk.security.crypto import Aes
#from deepdriver.sdk.interface.grpc_interface_pb2 import ArtifactEntry
import time
URL_CHECK_EMAIL = "/api/public/login/email"
URL_ID_LOGIN = "/api/public/login/pass"
URL_API_LOGIN = "/api/client/auth"
URL_CREATE = "/api/client/experiment/create"
URL_CREATE_HPO = "/api/client/experiment/create/hpo"
URL_CERATE_ARTIFACT ="/api/client/artifact/create"
URL_GET_HPO = "/api/client/experiment/get/hpo"
URL_UPLOAD_LOG = "/api/client/run/log/upload"
URL_UPLOAD_FILE = "/v1/res/file/upload"
URL_SEND_ALERT = "/api/client/run/alert/send"
URL_UPDATE_CONFIG = "/api/client/run/config/update"
URL_FINISH = "/api/client/run/finish"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

jwt_key: str = None
use_http: bool =True
cert_path: str = None

def set_jwt_key(jwt_key_: str) -> None:
    global jwt_key
    jwt_key = jwt_key_

def get_jwt_key() -> str:
    global jwt_key
    return jwt_key

def set_use_https(use_https_: bool) -> None:
    global use_http
    use_http = use_https_

def get_use_https() -> bool:
    global use_http
    return use_http

def set_cert_path(cert_path_: bool) -> None:
    global cert_path
    cert_path = cert_path_

def get_cert_path() -> str:
    global cert_path
    return cert_path


def login(http_host: str , api_key: str, id: str, pw: str, gtoken: str) -> Dict:

    if id!=None and pw!=None :
        data = {
            "email": id
        }
        url = parse_result_wraaper(http_host, get_use_https(),  URL_CHECK_EMAIL)
        rsp = post(url, data)
        if rsp["result"] == "success":
            encKey = rsp["encKey"]
            cipher= Aes(encKey)
            encrypt_pw = cipher.aes_encrypt('pkcs5', pw, 'ECB',None)

            url = parse_result_wraaper(http_host,  get_use_https(),URL_ID_LOGIN)
            data = {
                "email": id,
                "password": encrypt_pw,
                "signType": "NORML"
            }
            rsp = post(url, data)
            #logger.debug("login() " + rsp["message"])
            if rsp["result"] == "success":
                set_jwt_key(rsp["token"])
            return rsp
        else:
            return rsp
    elif gtoken is not None: #google login
        url = parse_result_wraaper(http_host, get_use_https(), URL_ID_LOGIN)
        data = {
            "email": id,
            "password": "",
            "gtoken": gtoken,
            "signType": "GOOGL"
        }
        rsp = post(url, data)
        #logger.debug("login() " + rsp["message"])
        if rsp["result"] == "success":
            set_jwt_key(rsp["token"])
        return rsp
    else:
        data = {
            "key": api_key
        }
        url = parse_result_wraaper(http_host, get_use_https(),URL_API_LOGIN)
        rsp = post(url, data)
        #logger.debug("login() " + rsp["message"])
        if rsp["result"] == "success":
            set_jwt_key(rsp["token"])
    return rsp

def init(http_host: str ,exp_name: str="", team_name: str="", run_name: str="", config: Dict=None) -> Dict:
    # Interface.py의 init 함수 호출시,
    # config 값을 넘겨주어 rest api의 인자인 config의 _custom 필드에 key, value값을 각각 넣어주도록 한다
    _custom = [{"key": k, "value": v} for k, v in config.items()] if config else []

    # sysInfo값을 넘겨주어 rest api의 인자인 sysInfo필드에 넣어주도록 한다
    sys_info = {
        "os": util.get_os(),
        "python": util.get_python_version(),
        "gpu": util.get_gpu(),
        "gpuCount": util.get_gpu_count(),
        "cpuCount": util.get_cpu_count(),
        "hostname": util.get_hostname(),
    }

    # Interface.py의 init 함수 호출 후 응답받은 데이터로 부터 실험환경 이름과 팀이름, 실행이름, 실행ID, 대쉬보드URL을 가져와 Run 객체에 설정하고 반환한다.
    data = {
        "teamName": team_name,
        "expName": exp_name,
        "runName": run_name,
        "config": {"cliVer": version.__version__, "pythonVer": util.get_python_version(), "_custom": _custom},
        "sysInfo": sys_info,
        "createRun": "Y",
    }

    url = parse_result_wraaper(http_host,  get_use_https(), URL_CREATE)
    rsp = post(url, data)
    logger.debug("init() response : " + rsp["message"])
    return rsp

def create_hpo(http_host:str, exp_name: str="", team_name: str="", hpo_config: Dict=None) -> Dict:

    data ={
        "teamName": team_name,
        "expName": exp_name,
        "config":  {"cliVer": version.__version__, "pythonVer": util.get_python_version(), "hpoConfig": hpo_config},
        "sysInfo": {
            "os": util.get_os(),
            "python": util.get_python_version(),
            "gpu": util.get_gpu(),
            "gpuCount": util.get_gpu_count(),
            "cpuCount": util.get_cpu_count(),
            "hostname": util.get_hostname(),
        },
    }
    url = parse_result_wraaper(http_host, get_use_https(), URL_CREATE_HPO)
    rsp = post(url, data)
    logger.debug("create_hpo() response : " + rsp["message"])
    return rsp


def get_hpo(http_host:str, exp_name: str="", team_name: str="") -> Dict:
    data = {
        "teamName": team_name,
        "expName": exp_name,
    }
    url = parse_result_wraaper(http_host, get_use_https(), URL_GET_HPO)
    rsp = post(url, data)
    logger.debug("get_hpo() response : " + rsp["message"])
    return rsp

def upload_log(http_host:str, run_id: int , exp_name: str, team_name: str , step: int , item_dict: Dict[str, Union[int, str, float, bool]] ) -> Dict:
    item_list = [{"key": k, "value": v} for k, v in item_dict.items()] if item_dict else []
    data = {
        "teamName": team_name,
        "expName": exp_name,
        "runId" : run_id,
        "step" : step,
        "items" :item_list,
    }
    url = parse_result_wraaper(http_host, get_use_https(), URL_UPLOAD_LOG)
    rsp = post(url, data)
    logger.debug("upload_log() response : " + rsp["message"])
    return rsp

def upload_file(http_host:str, upload_type: str, local_path: str, root_path: str, path: str, run_id: int,
                 teamName: str, expName: str, run_name: str,
                entry_digest: str, arti_info: ArtifactInfo, chunk_size:int, file_index: int) -> Dict:
    uplod_info =UploadInfo(upload_type=upload_type, local_path=local_path,root_path=root_path,path=path,run_id=run_id,teamName=teamName,expName=expName,run_name=run_name,entry_digest=entry_digest,file_index=file_index)
    url = parse_result_wraaper(http_host, get_use_https(),URL_UPLOAD_FILE) #TO-DO:
    def upload_callback(uploaded_size,total_size,local_path,entry_list,chunk_bytes, file_index):
        util.print_progress(uploaded_size, total_size, f'Uploading: [{local_path}]',
                            f"[{file_index + 1}/{1 if len(entry_list) == 0 else len(entry_list)}")
        if chunk_bytes == 0:  # Reached EOF
            util.print_progress(total_size, total_size, f'Uploading: [{local_path}]',
                                f"[{file_index + 1}/{1 if len(entry_list) == 0 else len(entry_list)}]")  # 100%
    with open(local_path, "rb") as f:
        progress = Progress(f,chunk_size,uplod_info,arti_info,upload_callback)
        for chunk in progress:
            chunk_data = chunk
            rsp=  post(
                url, data=chunk_data
            )
            logger.debug("upload_file() response : " + rsp["message"])
    logger.debug("upload_file() response : " + rsp["message"])
    return rsp

def create_artifact(http_host:str,teamName: str, expName: str, runId: int, arti_info : ArtifactInfo):

    data = {
        "teamName": teamName,
        "expName": expName,
        "artifactType" : arti_info.artifact_type,
        "artifactName" : arti_info.artifact_name,
        "artifactMode" : arti_info.artifact_mode,
        "artifactScope" : arti_info.artifact_scope,
        "artifactDescription": arti_info.artifact_description,
        "runId" : runId
    }
    url = parse_result_wraaper(http_host, get_use_https(), URL_CERATE_ARTIFACT)  # TO-DO:
    rsp = post(
        url, data=data
    )
    logger.debug("create_artifact() response : " + rsp["message"])
    return rsp
def update_config(http_host:str, run_id: int , exp_name: str, team_name: str , items: list):
    item_list = [{"key": k, "value": v} for (k, v) in items] if items else []
    data = {
        "teamName": team_name,
        "expName": exp_name,
        "runId" : run_id,
        "items" : item_list,
    }
    url = parse_result_wraaper(http_host, get_use_https(),URL_UPDATE_CONFIG)
    rsp = post(url, data)
    logger.debug("update_config() response : " + rsp["message"])
    return rsp

def send_alert(http_host:str, data: Dict ) -> Dict:
    url = parse_result_wraaper(http_host,get_use_https(),URL_SEND_ALERT)
    rsp = post(url, data)
    logger.debug("send_alert() response : " + rsp["result"])
    return rsp

def finish(http_host: str ,data: Dict) -> Dict:
    url = parse_result_wraaper(http_host,get_use_https(),URL_FINISH)
    rsp = post(url, data)
    logger.debug("finish() " + rsp["message"])
    return rsp

def post(url: str, data: Dict) -> Dict:
    logger.debug(f"REST[POST] to [{url}] : data=[{json.dumps(data)}], headers=[{get_headers()}")
    cert_path = get_cert_path()
    if cert_path is None:
        rsp = requests.post(url, headers=get_headers(), data=json.dumps(data) , verify= False)
    else:
        rsp = requests.post(url, headers=get_headers(), data=json.dumps(data), verify=cert_path)
    if rsp.status_code not in [200, 201]:
        if rsp.status_code in [503]:
            if cert_path is None:
                time.sleep(1)
                rsp = requests.post(url, headers=get_headers(), data=json.dumps(data), verify=False)
            else:
                rsp = requests.post(url, headers=get_headers(), data=json.dumps(data), verify=cert_path)
        logger.debug(f"post({url}) failed({rsp.status_code})")
        try:
            json_result = json.loads(rsp.text)  #json 파싱 실패 시
        except:
            raise Exception(f"request.post() failed({rsp.text if rsp.text else rsp.status_code})", rsp)

        if ('message' in json_result) and ('result' in json_result) and (json_result['result'] == 'fail'):
            if json.loads(rsp.text)['message'] == "INVALID KEY":
                logger.error("Invalid Login KEY.")
                raise Exception("Invalid Login KEY.")
            elif json.loads(rsp.text)['message'] == "invalid token":
                logger.error("Invalid Token.")
                raise Exception("Invalid Token.")
            else:
                raise Exception(f"request.post() failed({rsp.text if rsp.text else rsp.status_code})", rsp)
    return dict(json.loads(rsp.text))

def parse_result_wraaper(http_host, https, path):
    if https:
        scheme = "https"
    else:
        scheme = "http"
    return ParseResult(scheme=scheme, netloc=http_host, path=path, params='', query='', fragment='').geturl()
def get_headers():
    jwt_key = get_jwt_key()
    headers = {
        "Content-Type": "application/json",
    }
    if jwt_key:
        headers["Authorization"] = f"Bearer {jwt_key}"
    return headers
