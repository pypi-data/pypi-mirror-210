from assertpy import assert_that
from deepdriver.sdk.interface import interface
# deepdriver 실험환경을 사용하기위한 로그인 과정
# 서버의 login api를 호출하여 key를 서버로 전송하고 결과로서 jwt key를 받는다
def setting(http_host=None, use_grpc=False, grpc_host=None, use_grpc_tls=False , use_https=False, cert_file=None):
    if http_host is not None:
        interface.set_http_host(http_host,use_https)
    if grpc_host is not None:
        interface.set_grpc_host(grpc_host, use_grpc_tls)
    if cert_file is not None:
        interface.set_cert_path(cert_file)
    if use_grpc is not None:
        interface.set_use_grpc(use_grpc)
