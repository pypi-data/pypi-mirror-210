import os
import pickle
import re
import click
import grpc
from deepdriver.sdk.data_types.run import Run

from deepdriver.sdk.interface.http_interface import set_jwt_key

from deepdriver.sdk.interface.interface import set_stub

from deepdriver.sdk.interface.grpc_interface_pb2_grpc import ResourceStub

from deepdriver.cli.cli_ctx import Config


def check_is_setting(config):
    """ deepdriver setting 후 상태인지 확인 """
    if not config.http_host or not config.grpc_host:
        click.echo(click.style("Deepdriver Setting not exists. Set Deepdriver HTTP server and GRPC Server.", fg='red'))
        return False
    return True


def check_is_login(config):
    """ deepdriver login 후 상태인지 확인 """
    if not config.key or not config.token:
        click.echo(click.style("Deepdriver Login Ino not exists. Set Deepdriver Login First.", fg='red'))
        return False
    return True


def api_setting(config: Config):
    """ deepdriver setting """
    from deepdriver.sdk.interface.interface import set_http_host, set_grpc_host
    set_http_host(config.http_host)
    set_grpc_host(config.grpc_host)

def api_login(config: Config):
    """ deepdriver login """
    if config.use_grpc_tls:
        channel_opts = ()
        # channel_opts += ((
        #                      'grpc.ssl_target_name_override', "SERVER_NAME_TO_VERIFY",),)
        channel = grpc.secure_channel(config.grpc_host, grpc.ssl_channel_credentials(), channel_opts)
    else:
        channel = grpc.insecure_channel(config.grpc_host)
    stub = ResourceStub(channel)
    set_stub(stub)

    set_jwt_key(config.token)



def save_run_dump(path_dir, run:Run):
    with open(os.path.join(path_dir, "run"), 'wb') as f:  # run 객체를 dump함
        pickle.dump(run, f)

def load_run_file(path_dir):
    with open(os.path.join(path_dir, "run"), 'rb') as f:
        run = pickle.load(f)
        return run

def check_exp_name(exp_name):
    # raise click.BadParameter("Couldn't understand date.", param=exp_name)
    pattern = re.compile('[^a-zA-Z0-9._]+')
    if pattern.findall(exp_name):
        raise click.BadParameter("Experiment Name은 숫자(number), 영문자(alphabet), 언더바(_), 온점(.)만 가능합니다.",
                                 param=exp_name)
        return None
    if len(exp_name) >= 50:
        raise click.BadParameter("Experiment Name의 최대 길이는 50자 미만입니다. [max length 50]", param=exp_name)
        return None
    return exp_name


def test(ctx, param, value):
    """ argumenet callback test """
    # getattr(ctx.obj, ctx.obj.func_name)()
    return value
