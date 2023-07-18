from typing import Type

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def create_field_model(*, field: FieldInfo, name: str, model_name: str) -> Type[BaseModel]:
    """
    Creates a pydantic model for a specific field
    """
    params = {name.lower(): (field.annotation, field)}
    data_field_model: Type[BaseModel] = create_model(  # type: ignore[call-overload]
        __model_name=model_name, __config__={"arbitrary_types_allowed": True}, **params
    )
    return data_field_model
