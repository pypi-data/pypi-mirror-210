import configparser
import os
from typing import Dict

import click

from deepdriver.sdk.config import Config

import deepdriver
from deepdriver.sdk.data_types.run import Run, set_run
from deepdriver.sdk.interface import interface
from urllib.parse import urljoin


class Config(object):
    """ /deepdriver/settings/config.ini 파일을 읽고 쓰는 클래스 """

    def __init__(self):
        self.base_dir = os.getcwd()
        self.config_base_dir = os.path.join(self.base_dir, "deepdriver", "settings")
        self.config_file = os.path.join(self.config_base_dir, "config.ini")
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)  # config.ini 파일이 없으면 생성

        self.load()  # config.ini 파일을 읽어서 self.properties에 저장

    def load(self):
        self.properties = configparser.ConfigParser()
        self.properties.optionxform = str  # for uppercase
        self.properties.read(self.config_file)

    def save(self):
        with open(self.config_file, "w") as f:
            self.properties.write(f)

    @staticmethod
    def click_callback(ctx, param, value):
        getattr(ctx.obj, ctx.obj.func_name)()
        return value

    def get_value(self, section, key):
        if self.properties.has_option(section, key):
            return self.properties[section][key]
        else:
            return None

    @property
    def http_host(self) -> str:
        if self.properties.has_option("DEFAULT", "HTTP_HOST"):
            return self.properties["DEFAULT"]["HTTP_HOST"]
        else:
            return None

    @http_host.setter
    def http_host(self, host) -> str:
        self.properties.set("DEFAULT", "HTTP_HOST", host)

    @property
    def grpc_host(self) -> str:
        if self.properties.has_option("DEFAULT", "GRPC_HOST"):
            return self.properties["DEFAULT"]["GRPC_HOST"]
        else:
            return None

    @grpc_host.setter
    def grpc_host(self, host):
        self.properties.set("DEFAULT", "GRPC_HOST", host)

    @property
    def use_grpc_tls(self) -> bool:
        if self.properties.has_option("DEFAULT", "USE_GRPC_TLS"):
            return self.properties["DEFAULT"].getboolean("USE_GRPC_TLS")
        else:
            return False

    @use_grpc_tls.setter
    def use_grpc_tls(self, use_grpc_tls):
        self.properties["DEFAULT"]["USE_GRPC_TLS"] = str(use_grpc_tls)

    @property
    def key(self):
        if self.properties.has_option("USER", "KEY"):
            return self.properties["USER"]["KEY"]
        else:
            return None

    @key.setter
    def key(self, key):
        if self.properties.has_section("USER") is False:
            self.properties.add_section("USER")

        self.properties.set("USER", "KEY", key)

    @property
    def token(self):
        if self.properties.has_option("USER", "TOKEN"):
            return self.properties["USER"]["TOKEN"]
        else:
            return None

    @token.setter
    def token(self, token):
        if self.properties.has_section("USER") is False:
            self.properties.add_section("USER")

        self.properties.set("USER", "TOKEN", token)


class OptionDefaultFromContext(click.Option):
    def __init__(self, *args, **kwargs):
        self.default_section = kwargs.pop('default_section', None)
        self.default_key = kwargs.pop('default_key', None)
        self.default_value = kwargs.pop('default_value', None)
        super(OptionDefaultFromContext, self).__init__(*args, **kwargs)

    def get_default(self, ctx, **kwargs):
        config: Config = ctx.obj
        self.default = config.get_value(self.default_section, self.default_key)
        return super(OptionDefaultFromContext, self).get_default(ctx)

    def prompt_for_value(self, ctx):
        default = self.get_default(ctx)

        # only prompt if the default value is None
        if default is None:
            self.default = self.default_value
            return super(OptionDefaultFromContext, self).prompt_for_value(ctx)

        return default


class CommandGroup(click.Group):
    """This subclass of a group supports looking up aliases in a config
    file and with a bit of magic.
    """

    def get_command(self, ctx, cmd_name):
        # Step one: bulitin commands as normal
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # Step two: find the config object and ensure it's there.  This
        # will create the config object is missing.
        cfg = ctx.ensure_object(Config)

        # Step three: look up an explicit command alias in the config
        if cmd_name in cfg.aliases:
            actual_cmd = cfg.aliases[cmd_name]
            return click.Group.get_command(self, ctx, actual_cmd)

        # Alternative option: if we did not find an explicit alias we
        # allow automatic abbreviation of the command.  "status" for
        # instance will match "st".  We only allow that however if
        # there is only one command.
        matches = [
            x for x in self.list_commands(ctx) if x.lower().startswith(cmd_name.lower())
        ]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the command's name, not the alias
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args
