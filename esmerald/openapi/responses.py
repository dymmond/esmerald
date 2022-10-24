from http import HTTPStatus
from inspect import Signature
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Type, cast

from esmerald.datastructures import File, Redirect, Stream, Template
from esmerald.enums import MediaType
from esmerald.exceptions import (
    HTTPException,
    ImproperlyConfigured,
    ValidationErrorException,
)
from esmerald.openapi.enums import OpenAPIFormat, OpenAPIType
from esmerald.openapi.schema import create_schema
from esmerald.openapi.utils import pascal_case_to_text
from esmerald.responses import Response as EsmeraldResponse
from esmerald.utils.model import create_parsed_model_field
from openapi_schemas_pydantic.v3_1_0 import Response
from openapi_schemas_pydantic.v3_1_0.header import Header
from openapi_schemas_pydantic.v3_1_0.media_type import (
    MediaType as OpenAPISchemaMediaType,
)
from openapi_schemas_pydantic.v3_1_0.schema import Schema
from starlette.routing import get_name
from typing_extensions import get_args, get_origin

if TYPE_CHECKING:

    from esmerald.datastructures import Cookie
    from esmerald.routing.router import HTTPHandler
    from esmerald.types import AnyCallable
    from openapi_schemas_pydantic.v3_1_0.responses import Responses


def create_cookie_schema(cookie: "Cookie") -> Schema:
    cookie_copy = cookie.copy(update={"value": "<string>"})
    value = cookie_copy.to_header(header="")
    return Schema(description=cookie.description or "", example=value)


def create_success_response(handler: "HTTPHandler", create_examples: bool) -> Response:
    signature = Signature.from_callable(cast("AnyCallable", handler.fn))
    default_descriptions: Dict[Any, str] = {
        Stream: "Stream Response",
        Redirect: "Redirect Response",
        File: "File Download",
    }

    description = (
        handler.response_description
        or default_descriptions.get(signature.return_annotation)
        or HTTPStatus(handler.status_code).description
    )

    if signature.return_annotation not in {
        signature.empty,
        None,
        Redirect,
        File,
        Stream,
    }:
        return_annotation = signature.return_annotation
        if signature.return_annotation is Template:
            return_annotation = str
            handler.media_type = MediaType.HTML
        elif get_origin(signature.return_annotation) is EsmeraldResponse:
            return_annotation = get_args(signature.return_annotation)[0] or Any
        as_parsed_model_field = create_parsed_model_field(return_annotation)
        schema = create_schema(field=as_parsed_model_field, create_examples=create_examples)
        schema.contentEncoding = handler.content_encoding
        schema.contentMediaType = handler.content_media_type
        response = Response(
            content={handler.media_type: OpenAPISchemaMediaType(media_type_schema=schema)},
            description=description,
        )
    elif signature.return_annotation is Redirect:
        response = Response(
            content=None,
            description=description,
            headers={
                "location": Header(
                    param_schema=Schema(type=OpenAPIType.STRING),
                    description="target path for redirect",
                )
            },
        )
    elif signature.return_annotation in (File, Stream):
        response = Response(
            content={
                handler.media_type: OpenAPISchemaMediaType(
                    media_type_schema=Schema(
                        type=OpenAPIType.STRING,
                        contentEncoding=handler.content_encoding or "application/octet-stream",
                        contentMediaType=handler.content_media_type,
                    )
                )
            },
            description=description,
            headers={
                "content-length": Header(
                    param_schema=Schema(type=OpenAPIType.STRING),
                    description="File size in bytes",
                ),
                "last-modified": Header(
                    param_schema=Schema(
                        type=OpenAPIType.STRING, schema_format=OpenAPIFormat.DATE_TIME
                    ),
                    description="Last modified data-time in RFC 2822 format",
                ),
                "etag": Header(
                    param_schema=Schema(type=OpenAPIType.STRING),
                    description="Entity tag",
                ),
            },
        )
    else:
        response = Response(content=None, description=description)

    if response.headers is None:
        response.headers = {}

    for key, value in handler.get_response_headers().items():
        header = Header()
        for attribute_name, attribute_value in value.dict(exclude_none=True).items():
            if attribute_name == "value":
                model_field = create_parsed_model_field(type(attribute_value))
                header.param_schema = create_schema(field=model_field, create_examples=False)
        response.headers[key] = header
    cookies = handler.get_response_cookies()
    if cookies:
        response.headers["Set-Cookie"] = Header(
            param_schema=Schema(allOF=[create_cookie_schema(cookie=cookie) for cookie in cookies])
        )
    return response


def create_error_responses(
    exceptions: List[Type[HTTPException]],
) -> Iterator[Tuple[str, Response]]:

    grouped_exceptions: Dict[int, List[Type[HTTPException]]] = {}
    for exc in exceptions:
        if not grouped_exceptions.get(exc.status_code):
            grouped_exceptions[exc.status_code] = []
        grouped_exceptions[exc.status_code].append(exc)

    for status_code, exception_group in grouped_exceptions.items():
        exception_schemas = [
            Schema(
                type=OpenAPIType.OBJECT,
                required=["detail", "status_code"],
                properties=dict(
                    status_code=Schema(type=OpenAPIType.INTEGER),
                    detail=Schema(type=OpenAPIType.STRING),
                    extra=Schema(
                        type=[OpenAPIType.NULL, OpenAPIType.OBJECT, OpenAPIType.ARRAY],
                        additionalProperties=Schema(),
                    ),
                ),
                description=pascal_case_to_text((get_name(exc))),
                examples=[
                    {
                        "status_code": status_code,
                        "detail": HTTPStatus(status_code).phrase,
                        "extra": {},
                    }
                ],
            )
            for exc in exception_group
        ]

        if len(exception_schemas) > 1:
            schema = Schema(oneOf=exception_schemas)
        else:
            schema = exception_schemas[0]
        yield str(status_code), Response(
            description=HTTPStatus(status_code).description,
            content={MediaType.JSON: OpenAPISchemaMediaType(media_type_schema=schema)},
        )


def create_additional_responses(
    handler: "HTTPHandler",
) -> Iterator[Tuple[str, Response]]:
    if not handler.responses:
        return

    for status_code, additional_response in handler.responses.items():
        model_field = create_parsed_model_field(additional_response.model)
        schema = create_schema(
            field=model_field, create_examples=additional_response.create_examples
        )

        yield str(status_code), Response(
            description=additional_response.description,
            content={
                additional_response.media_type: OpenAPISchemaMediaType(media_type_schema=schema)
            },
        )


def create_responses(
    handler: "HTTPHandler", raises_validation_error: bool, create_examples: bool
) -> Optional["Responses"]:

    responses: "Responses" = {
        str(handler.status_code): create_success_response(
            handler=handler, create_examples=create_examples
        )
    }

    exceptions = handler.raise_exceptions or []
    if raises_validation_error and ValidationErrorException not in exceptions:
        exceptions.append(ValidationErrorException)

    for status_code, response in create_error_responses(exceptions):
        responses[status_code] = response

    for status_code, response in create_additional_responses(handler):
        if status_code in responses:
            raise ImproperlyConfigured(
                f"Additional response for status code {status_code} already exists in success or error responses"
            )
        responses[status_code] = response
    return responses or None
