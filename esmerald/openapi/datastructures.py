from typing import Type

from esmerald.enums import MediaType
from pydantic import BaseModel


class ResponseSpec(BaseModel):
    model: Type[BaseModel]
    create_examples: bool = True
    description: str = "Additional response"
    media_type: MediaType = MediaType.JSON
