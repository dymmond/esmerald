from typing import Optional, Type

from pydantic import BaseModel

from esmerald.enums import MediaType


class OpenAPIResponse(BaseModel):
    model: Type[BaseModel]
    create_examples: bool = True
    description: str = "Additional response"
    media_type: MediaType = MediaType.JSON
    status_text: Optional[str] = None
