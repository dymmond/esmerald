from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    FrozenSet,
    List,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from pydantic.v1.schema import (
    field_schema,
    get_flat_models_from_fields,
    get_model_name_map,
    model_process_schema,
)
from typing_extensions import Annotated, Literal, get_args, get_origin

from esmerald._openapi.constants import REF_PREFIX
from esmerald.typing import ModelMap

validation_error_definition = {
    "title": "ValidationError",
    "type": "object",
    "properties": {
        "loc": {
            "title": "Location",
            "type": "array",
            "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
        },
        "msg": {"title": "Message", "type": "string"},
        "type": {"title": "Error Type", "type": "string"},
    },
    "required": ["loc", "msg", "type"],
}

validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "detail": {
            "title": "Detail",
            "type": "array",
            "items": {"$ref": REF_PREFIX + "ValidationError"},
        }
    },
}

status_code_ranges: Dict[str, str] = {
    "1XX": "Information",
    "2XX": "Success",
    "3XX": "Redirection",
    "4XX": "Client Error",
    "5XX": "Server Error",
    "DEFAULT": "Default Response",
}


def get_schema_from_model_field(
    *,
    field: FieldInfo,
    schema_generator: GenerateJsonSchema,
    model_name_map: ModelMap,
    field_mapping: Dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
) -> Dict[str, Any]:
    return field_schema(  # type: ignore[no-any-return]
        field, model_name_map=model_name_map, ref_prefix=REF_PREFIX
    )[0]


def get_definitions(
    *,
    fields: List[FieldInfo],
    schema_generator: GenerateJsonSchema,
    model_name_map: ModelMap,
) -> Tuple[
    Dict[Tuple[FieldInfo, Literal["validation", "serialization"]], JsonSchemaValue],
    Dict[str, Dict[str, Any]],
]:
    models = get_flat_models_from_fields(fields, known_models=set())
    return {}, get_model_definitions(flat_models=models, model_name_map=model_name_map)


def get_model_definitions(
    *,
    flat_models: Set[Union[Type[BaseModel], Type[Enum]]],
    model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
) -> Dict[str, Any]:
    definitions: Dict[str, Dict[str, Any]] = {}
    for model in flat_models:
        m_schema, m_definitions, m_nested_models = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=REF_PREFIX
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        if "description" in m_schema:
            m_schema["description"] = m_schema["description"].split("\f")[0]
        definitions[model_name] = m_schema
    return definitions


@dataclass
class JsonSchema:  # type: ignore[no-redef]
    ref_template: str
