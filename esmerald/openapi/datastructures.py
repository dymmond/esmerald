from typing import List, Optional, Type, Union

from pydantic import BaseModel

from esmerald.enums import MediaType


class OpenAPIResponse(BaseModel):
    model: Union[Type[BaseModel], List[Type[BaseModel]]]
    description: str = "Additional response"
    media_type: MediaType = MediaType.JSON
    status_text: Optional[str] = None
