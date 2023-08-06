# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
from abc import abstractmethod
from os.path import expanduser

from es7s import APP_NAME
from es7s.shared import get_color, get_logger, format_attrs, run_subprocess, get_stderr
from es7s.shared.exception import ExecutableNotFoundError
from es7s.shared.path import RESOURCE_DIR, SHELL_COMMONS_FILE, USER_ES7S_BIN_DIR, SHELL_PATH


class _Invoker:
    def __init__(self, target: str):
        self._target = target

    def spawn(self, *args: str) -> None:
        cmd_target, cmd_args = self._get_spawn_cmd(*args)
        get_logger().info(f"Launching: {cmd_target} {format_attrs(cmd_args)}")
        code = os.spawnvpe(os.P_WAIT, cmd_target, cmd_args, self._build_env())
        if code == 127:
            raise ExecutableNotFoundError(self._target)

    def _get_spawn_cmd(self, *args: str) -> tuple[str, list]:
        return self._target, [self._target, *args]

    def get_help(self) -> str:
        cmd_target, cmd_args, cmd_shell = self._get_help_cmd()
        cp = run_subprocess(
            " ".join(cmd_args),
            executable=cmd_target,
            shell=cmd_shell,
            env=self._build_env(),
            timeout=10,
        )
        if cp.stderr:
            get_stderr().echo(cp.stderr)
        return cp.stdout

    def _get_help_cmd(self) -> tuple[str, list, bool]:
        return SHELL_PATH, [self._target, "--help"], True


    def _build_env(self) -> dict:
        import pkg_resources

        commons_rel_path = os.path.join(RESOURCE_DIR, SHELL_COMMONS_FILE)
        commons_path = pkg_resources.resource_filename(APP_NAME, commons_rel_path)
        theme_seq = get_color().get_theme_color().to_sgr()
        return {
            "PATH": self._build_path(),
            "ES7S_SHELL_COMMONS": commons_path,
            "ES7S_THEME_COLOR_SGR": ";".join(map(str, theme_seq.params)),
            # [@temp] filter out all G1/G2 es7s env vars:
            **{k: v for (k, v) in os.environ.items() if not k.lower().startswith("es7s")},
        }

    def _build_path(self) -> str:
        current = os.environ.get("PATH", "").split(":")
        filtered = ":".join(
            [
                # [@temp] remove all deprecated es7s parts from PATH too:
                *filter(lambda s: "es7s" not in s, current),
                # [@temp] restore legacy pathL
                expanduser("~/bin/es7s"),
                # add G3 path:
                USER_ES7S_BIN_DIR,
            ]
        )
        return filtered


class AutoInvoker(_Invoker):
    pass


class ShellInvoker(_Invoker):
    pass
