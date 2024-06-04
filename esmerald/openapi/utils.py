from typing import Any, Dict, List, Tuple, Union

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing_extensions import Literal

from esmerald.openapi.validation import (
    validation_error_definition,
    validation_error_response_definition,
)

VALIDATION_ERROR_DEFINITION = validation_error_definition.model_dump(exclude_none=True)
VALIDATION_ERROR_RESPONSE_DEFINITION = validation_error_response_definition.model_dump(
    exclude_none=True
)

STATUS_CODE_RANGES: Dict[str, str] = {
    "1XX": "Information",
    "2XX": "Success",
    "3XX": "Redirection",
    "4XX": "Client Error",
    "5XX": "Server Error",
    "DEFAULT": "Default Response",
}

ALLOWED_STATUS_CODE = {
    "default",
    "1XX",
    "2XX",
    "3XX",
    "4XX",
    "5XX",
}
REF_TEMPLATE = "#/components/schemas/{name}"


def get_definitions(
    *,
    fields: List[FieldInfo],
    schema_generator: GenerateJsonSchema,
) -> Tuple[
    Dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
    Dict[str, Dict[str, Any]],
]:
    inputs = [(field, "validation", TypeAdapter(field.annotation).core_schema) for field in fields]
    field_mapping, definitions = schema_generator.generate_definitions(
        inputs=inputs  # type: ignore
    )

    return field_mapping, definitions  # type: ignore[return-value]


def get_schema_from_model_field(
    *,
    field: FieldInfo,
    field_mapping: Dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> Dict[str, Any]:
    json_schema = field_mapping[(field, "validation")]
    if "$ref" not in json_schema:
        json_schema["title"] = field.title or field.alias.title().replace("_", " ")
    return json_schema


def is_status_code_allowed(status_code: Union[int, str, None]) -> bool:
    if status_code is None:
        return True
    if status_code in ALLOWED_STATUS_CODE:
        return True

    try:
        current_status_code = int(status_code)
    except ValueError:
        return False

    return not (current_status_code < 200 or current_status_code in {204, 304})


def dict_update(
    original_dict: Dict[Any, Any], update_dict: Dict[Any, Any]
) -> None:  # pragma: no cover
    for key, value in update_dict.items():
        if (
            key in original_dict
            and isinstance(original_dict[key], dict)
            and isinstance(value, dict)
        ):
            dict_update(original_dict[key], value)
        elif (
            key in original_dict
            and isinstance(original_dict[key], list)
            and isinstance(update_dict[key], list)
        ):
            original_dict[key] = original_dict[key] + update_dict[key]
        else:
            original_dict[key] = value
