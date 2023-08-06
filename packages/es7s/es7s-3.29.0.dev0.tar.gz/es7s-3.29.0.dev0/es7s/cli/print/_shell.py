# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import typing as t

import click

from es7s.cli._base_opts_params import CMDTYPE_INTEGRATED, CMDTRAIT_ADAPTIVE
from es7s.cli._invoker import ShellInvoker
from .._base import CliCommand
from .._decorators import _catch_and_log_and_exit, cli_command

SHELL_DIR_PATH = os.path.dirname(__file__)


class ShellCommandFactory:
    HELP_MAP = {
        "colors": ("xterm-16, xterm-256 and rgb color tables",),
        "ruler": ("Horizontal terminal char ruler.", CMDTRAIT_ADAPTIVE),
        "env-hosts": ("Remote hosts defined in env files.", ),
        "shell-param-exp": ("Shell parameter expansion cheatsheet.",),
    }

    def make_all(self) -> t.Iterable[click.Command]:
        for filename in os.listdir(SHELL_DIR_PATH):
            filepath = os.path.join(SHELL_DIR_PATH, filename)
            if not os.path.isfile(filepath) or os.path.splitext(filepath)[1] != ".sh":
                continue

            invoker = ShellInvoker(filepath)
            cmd = lambda ctx, inv=invoker: inv.spawn(*ctx.args)
            cmd = _catch_and_log_and_exit(cmd)
            cmd = click.pass_context(cmd)
            attributes = self.HELP_MAP.get(os.path.splitext(filename)[0], (f"{filename} script",))
            cmd = cli_command(
                name=filename,
                help=attributes[0],
                cls=CliCommand,
                type=CMDTYPE_INTEGRATED,
                traits=[*attributes[1:]],
                ignore_unknown_options=True,
                allow_extra_args=True,
                ext_help_invoker=lambda ctx, inv=invoker: inv.get_help(),
                usage_section_name="Usage (generic)",
                include_common_options_epilog=False,
            )(cmd)
            yield cmd
