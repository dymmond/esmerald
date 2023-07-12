from dataclasses import Field as DataclassField
from dataclasses import fields as get_dataclass_fields
from inspect import isclass
from typing import TYPE_CHECKING, Any, Dict, Tuple, Type, cast

from pydantic import BaseModel, ConfigDict, create_model

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo


config = ConfigDict(arbitrary_types_allowed=True)


def create_model_from_dataclass(dataclass: Any) -> Type[BaseModel]:
    """Creates a subclass of BaseModel from a given dataclass.

    We are limited here because Pydantic does not perform proper field
    parsing when going this route - which requires we set the fields as
    required and not required independently. We currently do not handle
    deeply nested Any and Optional.
    """
    dataclass_fields: Tuple[DataclassField, ...] = get_dataclass_fields(dataclass)
    model = create_model(dataclass.__name__, **{field.name: (field.type, ...) for field in dataclass_fields})  # type: ignore
    for field_name, model_field in model.model_fields.items():
        [field for field in dataclass_fields if field.name == field_name][0]
        setattr(model, field_name, model_field)
    return cast("Type[BaseModel]", model)


def create_parsed_model_field(value: Type[Any]) -> "FieldInfo":
    """Create a pydantic model with the passed in value as its sole field, and
    return the parsed field."""
    model = create_model("temp", __config__=config, **{"value": (value, ... if not repr(value).startswith("typing.Optional") else None)})  # type: ignore
    return cast("BaseModel", model).model_fields["value"]


_dataclass_model_map: Dict[Any, Type[BaseModel]] = {}


def convert_dataclass_to_model(dataclass: Any) -> Type[BaseModel]:
    """Converts a dataclass to a pydantic model and memoizes the result."""
    if not isclass(dataclass) and hasattr(dataclass, "__class__"):
        dataclass = dataclass.__class__
    if not _dataclass_model_map.get(dataclass):
        _dataclass_model_map[dataclass] = create_model_from_dataclass(dataclass)  # pyright: ignore
    return _dataclass_model_map[dataclass]
