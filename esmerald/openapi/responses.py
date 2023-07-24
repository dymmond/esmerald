from http import HTTPStatus
from inspect import Signature
from typing import TYPE_CHECKING, Any, Dict, Union, cast

from typing_extensions import get_args, get_origin

from esmerald.datastructures import File, Redirect, Stream, Template
from esmerald.enums import MediaType
from esmerald.openapi._internal import InternalResponse
from esmerald.responses import Response as EsmeraldResponse

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.routing.router import HTTPHandler
    from esmerald.typing import AnyCallable


def create_internal_response(
    handler: Union["HTTPHandler", Any]
) -> InternalResponse:  # pragma: no cover
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
            internal_response.media_type = MediaType.HTML
        elif get_origin(signature.return_annotation) is EsmeraldResponse:
            internal_response.return_annotation = get_args(signature.return_annotation)[0] or Any
            internal_response.media_type = handler.content_media_type
        else:
            internal_response.media_type = MediaType.JSON

        internal_response.encoding = handler.content_encoding

    elif signature.return_annotation is Redirect:
        internal_response.media_type = MediaType.JSON
    elif signature.return_annotation in (File, Stream):
        internal_response.media_type = handler.content_media_type
        internal_response.encoding = handler.content_encoding or MediaType.OCTET
    else:
        internal_response.media_type = handler.content_media_type
        internal_response.encoding = handler.content_encoding
    return internal_response
