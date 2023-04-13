from typing import Type

from pydantic import BaseModel

from esmerald.enums import MediaType


class ResponseSpecification(BaseModel):
    model: Type[BaseModel]
    create_examples: bool = True
    description: str = "Additional response"
    media_type: MediaType = MediaType.JSON
