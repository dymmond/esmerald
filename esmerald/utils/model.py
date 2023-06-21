from dataclasses import Field as DataclassField
from dataclasses import fields as get_dataclass_fields
from inspect import isclass
from typing import TYPE_CHECKING, Any, Dict, Tuple, Type, cast

from pydantic import BaseConfig, BaseModel, create_model

from esmerald.protocols.utils.protocols import DataclassProtocol

if TYPE_CHECKING:
    from pydantic.fields import ModelField


def set_model_field_to_required(model_field: "ModelField") -> "ModelField":
    """recursively sets the model_field and all sub_fields as required."""
    model_field.required = True
    if model_field.sub_fields:
        for index, sub_field in enumerate(model_field.sub_fields):
            model_field.sub_fields[index] = set_model_field_to_required(model_field=sub_field)
    return model_field


def create_model_from_dataclass(
    dataclass: Type["DataclassProtocol"],
) -> Type[BaseModel]:
    """Creates a subclass of BaseModel from a given dataclass.

    We are limited here because Pydantic does not perform proper field
    parsing when going this route - which requires we set the fields as
    required and not required independently. We currently do not handle
    deeply nested Any and Optional.
    """
    dataclass_fields: Tuple[DataclassField, ...] = get_dataclass_fields(
        dataclass
    )  # pyright: ignore
    model = create_model(dataclass.__name__, **{field.name: (field.type, ...) for field in dataclass_fields})  # type: ignore
    for field_name, model_field in model.__fields__.items():
        dataclass_field = [field for field in dataclass_fields if field.name == field_name][0]
        typing_string = repr(dataclass_field.type)
        model_field = set_model_field_to_required(model_field=model_field)
        if typing_string.startswith("typing.Optional") or typing_string == "typing.Any":
            model_field.required = False
            model_field.allow_none = True
            model_field.default = None
        else:
            model_field.required = True
            model_field.allow_none = False
        setattr(model, field_name, model_field)
    return cast("Type[BaseModel]", model)


class Config(BaseConfig):
    arbitrary_types_allowed = True


def create_parsed_model_field(value: Type[Any]) -> "ModelField":
    """Create a pydantic model with the passed in value as its sole field, and
    return the parsed field."""
    model = create_model("temp", __config__=Config, **{"value": (value, ... if not repr(value).startswith("typing.Optional") else None)})  # type: ignore
    return cast("BaseModel", model).__fields__["value"]


_dataclass_model_map: Dict[Any, Type[BaseModel]] = {}


def convert_dataclass_to_model(dataclass: Any) -> Type[BaseModel]:
    """Converts a dataclass to a pydantic model and memoizes the result."""
    if not isclass(dataclass) and hasattr(dataclass, "__class__"):
        dataclass = dataclass.__class__
    if not _dataclass_model_map.get(dataclass):
        _dataclass_model_map[dataclass] = create_model_from_dataclass(dataclass)  # pyright: ignore
    return _dataclass_model_map[dataclass]
