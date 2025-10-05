from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Reference(BaseModel):
    """A simple object to allow referencing other components in the OpenAPI
    document, internally and externally.

    The `$ref` string value contains a URI [RFC3986](https://tools.ietf.org/html/rfc3986),
    which identifies the location of the value being referenced.

    See the rules for resolving [Relative References](https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI).
    """

    ref: str = Field(alias="$ref")
    """**REQUIRED**. The reference identifier. This MUST be in the form of a URI."""

    summary: Optional[str] = None
    """
    A short summary which by default SHOULD override that of the referenced component.
    If the referenced object-type does not allow a `summary` field, then this field has no effect.
    """

    description: Optional[str] = None
    """
    A description which by default SHOULD override that of the referenced component.
    [CommonMark syntax](https://spec.commonmark.org/) MAY be used for rich text representation.
    If the referenced object-type does not allow a `description` field, then this field has no effect.
    """
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {"$ref": "#/components/schemas/Pet"},
                {"$ref": "Pet.json"},
                {"$ref": "definitions.json#/Pet"},
            ]
        },
    )
