# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import re

import click
import pytermor as pt

from es7s.shared import get_default_config, get_config, get_stdout, FrozenStyle
from .._decorators import cli_command, _catch_and_log_and_exit


@cli_command(
    name=__file__,
    short_help="display user/default config variables with values"
)
@_catch_and_log_and_exit
class ListCommand:
    """
    Display user [by default] config variables with values.\n\n

    Note the common option '--default' which affects this command as well;
    the default config values will be listed in that case.
    """

    HEADER_STYLE = FrozenStyle(fg=pt.cv.YELLOW)
    OPT_NAME_STYLE = FrozenStyle(fg=pt.cv.GREEN)
    OPT_VALUE_STYLE = FrozenStyle(bold=True)

    def __init__(self):
        self._run()

    def _run(self):
        config = get_config()
        stdout = get_stdout()
        for idx, section in enumerate(config.sections()):
            if idx > 0:
                stdout.echo()
            stdout.echo_rendered(f"[{section}]", self.HEADER_STYLE)
            for option in config.options(section):
                option_fmtd = stdout.render(option, self.OPT_NAME_STYLE)
                value_fmtd = self._render_value(config.get(section, option))
                stdout.echo_rendered(option_fmtd + " = " + value_fmtd)

    def _render_value(self, val: str) -> str:
        val = re.sub('\n+', '\n    ', val)
        return get_stdout().render(val, self.OPT_VALUE_STYLE)
