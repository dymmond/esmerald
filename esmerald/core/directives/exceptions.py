from typing import Any

from esmerald.exceptions import EsmeraldAPIException


class DirectiveError(EsmeraldAPIException):
    """
    Exception indicating a problem while executing a directive.
    """

    def __init__(self, detail: str, returncode: int = 1, **kwargs: Any):
        self.returncode = returncode
        super().__init__(detail=detail, **kwargs)
