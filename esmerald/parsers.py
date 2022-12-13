from contextlib import suppress
from typing import TYPE_CHECKING, Any

from esmerald.datastructures import UploadFile
from esmerald.enums import EncodingType
from orjson import JSONDecodeError, loads
from pydantic import BaseModel
from pydantic.fields import SHAPE_LIST, SHAPE_SINGLETON

if TYPE_CHECKING:
    from pydantic.fields import ModelField
    from pydantic.typing import DictAny
    from starlette.datastructures import FormData


class HashableBaseModel(BaseModel):
    """
    Pydantic BaseModel by default doesn't handle with hashable types the same way
    a python object would and therefore there are types that are mutable (list, set)
    not hashable and those need to be handled properly.

    HashableBaseModel handles those corner cases.
    """

    def __hash__(self):
        values = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))


class BaseModelExtra(BaseModel):
    """
    BaseModel that allows extra to be passed.
    """

    class Config:
        extra = "allow"


def validate_media_type(field: "ModelField", values: "DictAny"):
    """
    Validates the media type against the available types.
    """
    if field.shape in SHAPE_LIST:
        return list(values.values())
    if field.shape in SHAPE_SINGLETON and field.type_in[UploadFile] and values:
        return list(values.values())[0]


def parse_form_data(media_type: "EncodingType", form_data: "FormData", field: "ModelField") -> Any:
    values: "DictAny" = {}
    for key, value in form_data.multi_items():
        if not isinstance(value, UploadFile):
            with suppress(JSONDecodeError):
                value = loads(value)
        if isinstance(value, UploadFile):
            value = UploadFile(
                filename=value.filename,
                file=value.file,
                content_type=value.content_type,
                headers=value.headers,
            )
        if values.get(key):
            if isinstance(values[key], list):
                values[key].append(value)
            else:
                values[key] = [values[key], value]
        else:
            values[key] = value
    if media_type == EncodingType.MULTI_PART:
        return validate_media_type(field=field, values=values)
    return values
