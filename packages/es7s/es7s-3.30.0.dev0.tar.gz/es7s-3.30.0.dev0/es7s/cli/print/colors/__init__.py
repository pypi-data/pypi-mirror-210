# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import click

from .. import _shell
from . import hsv
from ..._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__)
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """Color sheets."""


group.add_commands(
    *_shell.ShellCommandFactory()._get_by_dir("colors"),
    hsv.PrintColors256Command,
)
