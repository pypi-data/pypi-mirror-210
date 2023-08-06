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
        ("colors", "legacy"): ("xterm-16, xterm-256 and rgb color tables",),
        ("", "ruler"): ("Horizontal terminal char ruler.", CMDTRAIT_ADAPTIVE),
        ("", "env-hosts"): ("Remote hosts defined in env files.", ),
        ("", "shell-param-exp"): ("Shell parameter expansion cheatsheet.",),
    }

    _cmds: dict[str, list[ShellInvoker]] = dict()

    def __init__(self):
        if not ShellCommandFactory._cmds:
            self._iter_dir(None)

    def _get_by_dir(self, dirname: str = None) -> list[ShellInvoker]:
        return ShellCommandFactory._cmds.get(dirname, [])

    def _iter_dir(self, dirname: str = None) -> None:
        absdirname = os.path.join(SHELL_DIR_PATH, dirname or "")
        for filename in os.listdir(absdirname):
            filepath = os.path.join(absdirname, filename)
            if os.path.isdir(filepath):
                self._iter_dir(filename)
            if not os.path.isfile(filepath) or os.path.splitext(filepath)[1] != ".sh":
                continue

            invoker = ShellInvoker(filepath)
            cmd = lambda ctx, inv=invoker: inv.spawn(*ctx.args)
            cmd = _catch_and_log_and_exit(cmd)
            cmd = click.pass_context(cmd)
            attributes = self.HELP_MAP.get(
                (os.path.basename(dirname or ""), os.path.splitext(filename)[0]),
                (f"{filename} script",),
            )
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

            if not ShellCommandFactory._cmds.get(dirname):
                ShellCommandFactory._cmds[dirname] = []
            ShellCommandFactory._cmds[dirname].append(cmd)
