from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .operation import Operation
from .parameter import Parameter
from .reference import Reference
from .server import Server


class PathItem(BaseModel):
    """Describes the operations available on a single path.

    A Path Item MAY be empty, due to [ACL constraints](https://spec.openapis.org/oas/v3.1.0#securityFiltering).
    The path itself is still exposed to the documentation viewer
    but they will not know which operations and parameters are available.
    """

    ref: Optional[str] = Field(default=None, alias="$ref")
    """
    Allows for an external definition of this path item.
    The referenced structure MUST be in the format of a [Path Item Object](https://spec.openapis.org/oas/v3.1.0#pathItemObject).

    In case a Path Item Object field appears both in the defined object and the referenced object,
    the behavior is undefined.
    See the rules for resolving [Relative References](https://spec.openapis.org/oas/v3.1.0#relativeReferencesURI).
    """

    summary: Optional[str] = None
    """
    An optional, string summary, intended to apply to all operations in this path.
    """

    description: Optional[str] = None
    """
    An optional, string description, intended to apply to all operations in this path.
    [CommonMark syntax](https://spec.commonmark.org/) MAY be used for rich text representation.
    """

    get: Optional[Operation] = None
    """
    A definition of a GET operation on this path.
    """

    put: Optional[Operation] = None
    """
    A definition of a PUT operation on this path.
    """

    post: Optional[Operation] = None
    """
    A definition of a POST operation on this path.
    """

    delete: Optional[Operation] = None
    """
    A definition of a DELETE operation on this path.
    """

    options: Optional[Operation] = None
    """
    A definition of a OPTIONS operation on this path.
    """

    head: Optional[Operation] = None
    """
    A definition of a HEAD operation on this path.
    """

    patch: Optional[Operation] = None
    """
    A definition of a PATCH operation on this path.
    """

    trace: Optional[Operation] = None
    """
    A definition of a TRACE operation on this path.
    """

    servers: Optional[list[Server]] = None
    """
    An alternative `server` array to service all operations in this path.
    """

    parameters: Optional[list[Union[Parameter, Reference]]] = None
    """
    A list of parameters that are applicable for all the operations described under this path.
    These parameters can be overridden at the operation level, but cannot be removed there.
    The list MUST NOT include duplicated parameters.
    A unique parameter is defined by a combination of a [name](https://spec.openapis.org/oas/v3.1.0#parameterName) and [location](https://spec.openapis.org/oas/v3.1.0#parameterIn).
    The list can use the [Reference Object](https://spec.openapis.org/oas/v3.1.0#referenceObject) to link to parameters that are defined at the
    [OpenAPI Object's components/parameters](https://spec.openapis.org/oas/v3.1.0#componentsParameters).
    """
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "get": {
                        "description": "Returns pets based on ID",
                        "summary": "Find pets by ID",
                        "operationId": "getPetsById",
                        "responses": {
                            "200": {
                                "description": "pet response",
                                "content": {
                                    "*/*": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Pet"},
                                        }
                                    }
                                },
                            },
                            "default": {
                                "description": "error payload",
                                "content": {
                                    "text/html": {
                                        "schema": {"$ref": "#/components/schemas/ErrorModel"}
                                    }
                                },
                            },
                        },
                    },
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "description": "ID of pet to use",
                            "required": True,
                            "schema": {"type": "array", "items": {"type": "string"}},
                            "style": "simple",
                        }
                    ],
                }
            ]
        },
    )
