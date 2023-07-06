from typing import TYPE_CHECKING, Optional

from openapi_schemas_pydantic.v3_1_0.media_type import MediaType as OpenAPIMediaType
from openapi_schemas_pydantic.v3_1_0.request_body import RequestBody

from esmerald.enums import EncodingType
from esmerald.openapi.schema import create_schema, update_schema_field_info

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo as FieldInfo


def create_request_body(field: "FieldInfo", create_examples: bool) -> Optional[RequestBody]:
    """
    Gets the request body of the handler.
    """
    extra = field.json_schema_extra or {}
    media_type = extra.get("media_type", EncodingType.JSON)
    schema = create_schema(field=field, create_examples=create_examples)
    update_schema_field_info(schema=schema, field_info=field)
    return RequestBody(
        required=True, content={media_type: OpenAPIMediaType(media_type_schema=schema)}  # type: ignore[call-arg]
    )
