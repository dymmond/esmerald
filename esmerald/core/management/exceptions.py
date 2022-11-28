from typing import TYPE_CHECKING

from esmerald.exceptions import EsmeraldAPIException

if TYPE_CHECKING:
    from pydantic.typing import DictAny


class DirectiveError(EsmeraldAPIException):
    """
    Exception indicating a problem while executing a directive.
    """

    def __init__(self, detail: str, returncode: int = 1, **kwargs: "DictAny"):
        self.returncode = returncode
        super().__init__(detail=detail, **kwargs)


class SystemCheckError(DirectiveError):

    ...
