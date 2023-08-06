# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from es7s.shared.sub import run_detached
from .._decorators import cli_command, _catch_and_log_and_exit
from ...shared import get_user_config_filepath, get_stdout
from ...shared.config import get_default_config_filepath
from ...shared.path import GIT_PATH


@cli_command(name=__file__, short_help="show differences between current and default configs")
@_catch_and_log_and_exit
class DiffCommand:
    """
    Compare current user config with the default one and show the differences.\n\n

    This command requires ++git++ to be present and available.
    """

    def __init__(self):
        self._run()

    def _run(self):
        default_config_filepath = get_default_config_filepath()
        user_config_filepath = get_user_config_filepath()

        color_args = ["--color", "--color-moved"] if get_stdout().sgr_allowed else []
        run_detached(
            [
                GIT_PATH,
                "diff",
                "--no-index",
                "--minimal",
                "--ignore-all-space",
                *color_args,
                default_config_filepath,
                user_config_filepath,
            ]
        )
        get_stdout().echo("Done")
