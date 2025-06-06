from typing import Optional, Union

from pydantic import BaseModel, ConfigDict

from .callback import Callback
from .example import Example
from .header import Header
from .link import Link
from .parameter import Parameter
from .path_item import PathItem
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .schema import Schema
from .security_scheme import SecurityScheme


class Components(BaseModel):
    """Holds a set of reusable objects for different aspects of the OAS.

    All objects defined within the components object will have no effect
    on the API unless they are explicitly referenced from properties
    outside the components object.
    """

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "examples": [
                {
                    "schemas": {
                        "GeneralError": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "integer", "format": "int32"},
                                "message": {"type": "string"},
                            },
                        },
                        "Category": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "format": "int64"},
                                "name": {"type": "string"},
                            },
                        },
                        "Tag": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "format": "int64"},
                                "name": {"type": "string"},
                            },
                        },
                    },
                    "parameters": {
                        "skipParam": {
                            "name": "skip",
                            "in": "query",
                            "description": "number of items to skip",
                            "required": True,
                            "schema": {"type": "integer", "format": "int32"},
                        },
                        "limitParam": {
                            "name": "limit",
                            "in": "query",
                            "description": "max records to return",
                            "required": True,
                            "schema": {"type": "integer", "format": "int32"},
                        },
                    },
                    "responses": {
                        "NotFound": {"description": "Entity not found."},
                        "IllegalInput": {"description": "Illegal input for operation."},
                        "GeneralError": {
                            "description": "General Error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GeneralError"}
                                }
                            },
                        },
                    },
                    "securitySchemes": {
                        "api_key": {"type": "apiKey", "name": "api_key", "in": "header"},
                        "petstore_auth": {
                            "type": "oauth2",
                            "flows": {
                                "implicit": {
                                    "authorizationUrl": "http://example.org/api/oauth/dialog",
                                    "scopes": {
                                        "write:pets": "modify pets in your account",
                                        "read:pets": "read your pets",
                                    },
                                }
                            },
                        },
                    },
                }
            ]
        },
    )

    schemas: Optional[dict[str, Schema]] = None
    """An object to hold reusable [Schema Objects](https://spec.openapis.org/oas/v3.1.0#schemaObject)."""

    responses: Optional[dict[str, Union[Response, Reference]]] = None
    """An object to hold reusable [Response Objects](https://spec.openapis.org/oas/v3.1.0#responseObject)."""

    parameters: Optional[dict[str, Union[Parameter, Reference]]] = None
    """An object to hold reusable [Parameter Objects](https://spec.openapis.org/oas/v3.1.0#parameterObject)."""

    examples: Optional[dict[str, Union[Example, Reference]]] = None
    """An object to hold reusable [Example Objects](https://spec.openapis.org/oas/v3.1.0#exampleObject)."""

    requestBodies: Optional[dict[str, Union[RequestBody, Reference]]] = None
    """An object to hold reusable [Request Body Objects](https://spec.openapis.org/oas/v3.1.0#requestBodyObject)."""

    headers: Optional[dict[str, Union[Header, Reference]]] = None
    """An object to hold reusable [Header Objects](https://spec.openapis.org/oas/v3.1.0#headerObject)."""

    securitySchemes: Optional[dict[str, Union[SecurityScheme, Reference]]] = None
    """An object to hold reusable [Security Scheme Objects](https://spec.openapis.org/oas/v3.1.0#securitySchemeObject)."""

    links: Optional[dict[str, Union[Link, Reference]]] = None
    """An object to hold reusable [Link Objects](https://spec.openapis.org/oas/v3.1.0#linkObject)."""

    callbacks: Optional[dict[str, Union[Callback, Reference]]] = None
    """An object to hold reusable [Callback Objects](https://spec.openapis.org/oas/v3.1.0#callbackObject)."""

    pathItems: Optional[dict[str, Union[PathItem, Reference]]] = None
    """An object to hold reusable [Path Item Object](https://spec.openapis.org/oas/v3.1.0#pathItemObject)."""
