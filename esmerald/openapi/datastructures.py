from typing import List, Optional, Type, Union

from pydantic import BaseModel, field_validator

from esmerald.enums import MediaType


class OpenAPIResponse(BaseModel):
    model: Union[Type[BaseModel], List[Type[BaseModel]]]
    description: str = "Additional response"
    media_type: MediaType = MediaType.JSON
    status_text: Optional[str] = None

    @field_validator("model", mode="before")
    def validate_model(
        cls, model: Union[Type[BaseModel], List[Type[BaseModel]]]
    ) -> Union[Type[BaseModel], List[Type[BaseModel]]]:
        if isinstance(model, list) and len(model) > 1:
            raise ValueError(
                "The representation of a list of models in OpenAPI can only be a total of one. Example: OpenAPIResponse(model=[MyModel])."
            )
        return model
