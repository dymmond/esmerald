from http import HTTPStatus
from inspect import Signature
from typing import TYPE_CHECKING, Any, Union, cast

from typing_extensions import get_args, get_origin

from ravyn.core.datastructures import File, Redirect, Stream, Template
from ravyn.openapi._internal import InternalResponse
from ravyn.responses import Response as RavynResponse
from ravyn.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.routing.router import HTTPHandler
    from ravyn.typing import AnyCallable as AnyCallable  # noqa


def create_internal_response(
    handler: Union["HTTPHandler", Any],
) -> InternalResponse:  # pragma: no cover
    signature = Signature.from_callable(cast("AnyCallable", handler.fn))
    default_descriptions: dict[Any, str] = {
        Stream: "Stream Response",
        Redirect: "Redirect Response",
        File: "File Download",
    }

    description = (
        handler.response_description
        or default_descriptions.get(signature.return_annotation)
        or HTTPStatus(handler.status_code).description
    )

    internal_response = InternalResponse(
        description=description, signature=signature, return_annotation=signature.return_annotation
    )

    if signature.return_annotation not in {
        signature.empty,
        None,
        Redirect,
        File,
        Stream,
    }:
        if signature.return_annotation is Template:
            internal_response.return_annotation = str
            internal_response.media_type = (
                handler.content_media_type or handler.media_type or MediaType.HTML
            )
        elif get_origin(signature.return_annotation) is RavynResponse:
            internal_response.return_annotation = get_args(signature.return_annotation)[0] or Any
            internal_response.media_type = handler.content_media_type
        else:
            internal_response.media_type = handler.content_media_type or MediaType.JSON

        internal_response.encoding = handler.content_encoding

    elif signature.return_annotation is Redirect:
        internal_response.media_type = MediaType.JSON
    elif signature.return_annotation in (File, Stream):
        internal_response.media_type = handler.content_media_type or MediaType.OCTET
        internal_response.encoding = handler.content_encoding
    else:
        internal_response.media_type = handler.content_media_type
        internal_response.encoding = handler.content_encoding
    return internal_response
