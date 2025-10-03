from typing import Optional

from pydantic import AnyUrl, BaseModel, ConfigDict


class ExternalDocumentation(BaseModel):
    """Allows referencing an external resource for extended documentation."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "examples": [{"description": "Find more info here", "url": "https://example.com"}]
        },
    )

    description: Optional[str] = None
    """
    A short description of the target documentation.
    [CommonMark syntax](https://spec.commonmark.org/) MAY be used for rich text representation.
    """

    url: AnyUrl
    """
    **REQUIRED**. The URL for the target documentation.
    Value MUST be in the form of a URL.
    """
