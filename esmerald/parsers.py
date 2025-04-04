from contextlib import suppress
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Dict, List, get_args, get_origin

from lilya.datastructures import DataUpload as LilyaUploadFile
from orjson import loads
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from esmerald.core.datastructures import UploadFile
from esmerald.utils.enums import EncodingType

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


class ArbitraryBaseModel(BaseModel):
    """
    ArbitraryBaseModel that allows arbitrary_types_allowed to be passed.
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


def parse_json_value(value: Any) -> Any:
    """
    Attempts to parse a JSON string into a Python object.

    If parsing fails, returns the original value.

    Args:
        value (Any): The value to be parsed.

    Returns:
        Any: Parsed JSON object or the original value.
    """
    if not isinstance(value, str):
        return value

    with suppress(JSONDecodeError):
        return loads(value)

    return value  # type: ignore


def merge_values(values_dict: Dict[str, Any], key: str, value: Any) -> None:
    """
    Merges values into a dictionary, ensuring that multiple values for the same key
    are stored in a list.

    Args:
        values_dict (Dict[str, Any]): The dictionary storing parsed form data.
        key (str): The key for the form field.
        value (Any): The value to be added.
    """
    if key in values_dict:
        existing_value = values_dict[key]
        if isinstance(existing_value, list):
            existing_value.append(value)
        else:
            values_dict[key] = [existing_value, value]
    else:
        values_dict[key] = value


def process_form_data(form_data: "FormData") -> Dict[str, Any]:
    """
    Processes form data, converting JSON-encoded strings and organizing values into a dictionary.

    Args:
        form_data (FormData): The form data to be processed.

    Returns:
        Dict[str, Any]: Parsed and structured form data.
    """
    values_dict: Dict[str, Any] = {}

    for key, value in form_data.multi_items():
        parsed_value = value if isinstance(value, LilyaUploadFile) else parse_json_value(value)
        merge_values(values_dict, key, parsed_value)

    return values_dict


def handle_multipart_encoding(field: "FieldInfo", values_dict: Dict[str, Any]) -> Any:
    """
    Handles parsing of multipart form data based on field annotations.

    Args:
        field (FieldInfo): Field metadata including expected data types.
        values_dict (Dict[str, Any]): Parsed form data.

    Returns:
        Any: The processed value, formatted correctly according to field type.
    """
    if not values_dict:
        return None

    # If the field expects a list, flatten the values
    if get_origin(field.annotation) is list:
        return flatten(list(values_dict.values()))

    # Handle direct UploadFile types
    if field.annotation in (LilyaUploadFile, UploadFile):
        return list(values_dict.values())[0]

    # Check if UploadFile is inside a Union (e.g., Optional[UploadFile])
    for arg in get_args(field.annotation):
        if issubclass(arg, (LilyaUploadFile, UploadFile)):
            return list(values_dict.values())[0]

    return values_dict


def parse_form_data(
    media_type: "EncodingType", form_data: "FormData", field: "FieldInfo"
) -> Any:  # pragma: no cover
    """
    Parses form data by converting JSON-encoded fields, merging multiple values,
    and handling multipart encoding appropriately.

    Args:
        media_type (EncodingType): The encoding type of the form data.
        form_data (FormData): The form data containing key-value pairs.
        field (FieldInfo): Metadata defining the expected data structure.

    Returns:
        Any: Parsed form data in an appropriate format, based on the field type.
    """
    values_dict = process_form_data(form_data)

    if media_type == EncodingType.MULTI_PART:
        return handle_multipart_encoding(field, values_dict)

    return values_dict if values_dict else None
