# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

class NotInitializedError(RuntimeError):
    def __init__(self, source: object) -> None:
        self._source = source
        super().__init__(f"{source.__class__.__qualname__} is not initialized")


class ExecutableNotFoundError(RuntimeError):
    def __init__(self, path: str) -> None:
        self._path = path
        super().__init__(f"Executable not found: '{path}'")


class ArgCountError(Exception):
    def __init__(self, actual: int, *expected: int) -> None:
        expected_str = ", ".join(str(e) for e in expected)
        msg = f"Invalid arguments amount, expected one of: ({expected_str}), got: {actual}"
        super().__init__(msg)
