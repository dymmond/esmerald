from contextlib import suppress
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING, Any, Dict, List, get_args, get_origin

from lilya.datastructures import DataUpload as LilyaUploadFile
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from esmerald.datastructures import UploadFile
from esmerald.enums import EncodingType

if TYPE_CHECKING:  # pragma: no cover
    from lilya.datastructures import FormData


class HashableBaseModel(BaseModel):  # pragma: no cover
    """
    Pydantic BaseModel by default doesn't handle with hashable types the same way
    a python object would and therefore there are types that are mutable (list, set)
    not hashable and those need to be handled properly.

    HashableBaseModel handles those corner cases.
    """

    def __hash__(self) -> int:
        values: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            values[key] = None
            if isinstance(value, (list, set)):
                values[key] = tuple(value)
            else:
                values[key] = value
        return hash((type(self),) + tuple(values))


class ArbitraryHashableBaseModel(HashableBaseModel):
    """
    Same as HashableBaseModel but allowing arbitrary values
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class BaseModelExtra(BaseModel):
    """
    BaseModel that allows extra to be passed.
    """

    model_config = ConfigDict(extra="allow")


class ArbitraryBaseModel(BaseModel):
    """
    ArbitratyBaseModel that allows arbitrary_types_allowed to be passed.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ArbitraryExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


def flatten(values: List[Any]) -> List[Any]:
    """
    Flattens a list
    """
    flattened = []

    for value in values:
        if isinstance(value, list):
            flattened.extend(flatten(value))
        else:
            flattened.append(value)
    return flattened


def parse_form_data(
    media_type: "EncodingType", form_data: "FormData", field: "FieldInfo"
) -> Any:  # pragma: no cover
    """
    Converts, parses and transforms a multidict into a dict and tries to load them all into
    json.
    """
    values_dict: Dict[str, Any] = {}
    for key, value in form_data.multi_items():
        if not isinstance(value, LilyaUploadFile):
            with suppress(JSONDecodeError):
                value = loads(value)
        value_in_dict = values_dict.get(key)
        if isinstance(value_in_dict, list):
            values_dict[key].append(value)
        elif value_in_dict:
            values_dict[key] = [value_in_dict, value]
        else:
            values_dict[key] = value

    if media_type == EncodingType.MULTI_PART:
        if get_origin(field.annotation) is list:
            values = list(values_dict.values())
            return flatten(values=values)
        if field.annotation in (LilyaUploadFile, UploadFile) and values_dict:
            return list(values_dict.values())[0]

        # Check the arguments if there is any MULTI_PART in a possible Union with UploadFile
        # and a None (Optional).
        for arg in get_args(field.annotation):
            if issubclass(arg, (LilyaUploadFile, UploadFile)) and values_dict:
                return list(values_dict.values())[0]

    return values_dict if values_dict else None
