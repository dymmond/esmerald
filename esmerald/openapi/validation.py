from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from esmerald.openapi.constants import REF_PREFIX


class BaseDetail(BaseModel):
    title: str
    type: str
    items: Dict[str, Any]


class Detail(BaseDetail): ...


class Loc(BaseDetail): ...


class Property(BaseModel):
    loc: Optional[Loc] = None
    msg: Optional[Dict[str, str]] = None
    type: Optional[Dict[str, str]] = None
    detail: Optional[Detail] = None


class ValidationErrorModel(BaseModel):
    title: str
    type: str
    properties: Property
    required: Optional[List[str]] = None


validation_error_definition = ValidationErrorModel(
    title="ValidationError",
    type="object",
    properties=Property(
        loc=Loc(
            title="Location",
            type="array",
            items={"anyOf": [{"type": "string"}, {"type": "integer"}]},
        ),
        msg={"title": "Message", "type": "string"},
        type={"title": "Error Type", "type": "string"},
    ),
    required=["loc", "msg", "type"],
)

validation_error_response_definition = ValidationErrorModel(
    title="HTTPValidationError",
    type="object",
    properties=Property(
        detail=Detail(title="Detail", type="array", items={"$ref": REF_PREFIX + "ValidationError"})
    ),
)
