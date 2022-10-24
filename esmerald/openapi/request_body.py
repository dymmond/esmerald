from typing import TYPE_CHECKING, Optional

from esmerald.enums import EncodingType
from esmerald.openapi.schema import create_schema, update_schema_field_info
from openapi_schemas_pydantic.v3_1_0.media_type import MediaType as OpenAPIMediaType
from openapi_schemas_pydantic.v3_1_0.request_body import RequestBody

if TYPE_CHECKING:
    from pydantic.fields import ModelField


def create_request_body(field: "ModelField", create_examples: bool) -> Optional[RequestBody]:
    """
    Gets the request body of the handler.
    """
    media_type = field.field_info.extra.get("media_type", EncodingType.JSON)
    schema = create_schema(field=field, create_examples=create_examples)
    update_schema_field_info(schema=schema, field_info=field.field_info)
    return RequestBody(
        required=True, content={media_type: OpenAPIMediaType(media_type_schema=schema)}
    )
