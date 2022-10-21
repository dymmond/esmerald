import re
from typing import TYPE_CHECKING, Type

from esmerald.exceptions import ImproperlyConfigured
from esmerald.openapi.constants import PYDANTIC_FIELD_SHAPE_MAP
from openapi_schema_pydantic.v3.v3_1_0.schema import Schema
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.fields import ModelField
    from starlite.openapi.enums import OpenAPIType

CAPITAL_LETTERS_PATTERN = re.compile(r"(?=[A-Z])")


class OpenAPI310PydanticSchema(Schema):
    schema_class: Type[BaseModel]


def pascal_case_to_text(string: str) -> str:
    """Given a 'PascalCased' string, return its split form- 'Pascal Cased'."""
    return " ".join(re.split(CAPITAL_LETTERS_PATTERN, string)).strip()


def get_openapi_type_for_complex_type(field: "ModelField") -> "OpenAPIType":
    """We are dealing with complex types in this case.

    The problem here is that the Python typing system is too crude to
    define OpenAPI objects properly.
    """
    try:
        return PYDANTIC_FIELD_SHAPE_MAP[field.shape]
    except KeyError as e:
        raise ImproperlyConfigured(
            f"Parameter '{field.name}' with type '{field.outer_type_}' could not be mapped to an Open API type. "
            f"This can occur if a user-defined generic type is resolved as a parameter. If '{field.name}' should "
            "not be documented as a parameter, annotate it using the `Dependency` function, e.g., "
            f"`{field.name}: ... = Dependency(...)`."
        ) from e
