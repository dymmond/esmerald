from inspect import Signature
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict

from esmerald.utils.enums import MediaType


class InternalResponse(BaseModel):
    """
    Response generated for non common return types.
    """

    media_type: Optional[Union[str, MediaType]] = None
    return_annotation: Optional[Any] = None
    signature: Optional[Signature] = None
    description: Optional[str] = None
    encoding: Optional[str] = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(annotation={self.media_type}, default={self.encoding})"
