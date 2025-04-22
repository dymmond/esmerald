from typing import Any, Dict, List, Optional, TypeVar, Union

from pydantic import DirectoryPath, validate_call
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class TemplateProtocol(Protocol):  # pragma: no cover
    def make_response(self, **context: Optional[Dict[str, Any]]) -> str: ...


TP = TypeVar("TP", bound=TemplateProtocol, covariant=True)


@runtime_checkable
class TemplateEngineProtocol(Protocol[TP]):  # pragma: no cover
    @validate_call
    def __init__(
        self, directory: Union[DirectoryPath, List[DirectoryPath]], **kwargs: Any
    ) -> None: ...

    def get_template(self, template_name: str) -> TP: ...

    def get_template_render_function(self) -> str: ...
