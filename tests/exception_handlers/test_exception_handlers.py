from typing import Type

import pytest
from lilya.status import HTTP_400_BAD_REQUEST

from esmerald.applications import ChildEsmerald
from esmerald.enums import MediaType
from esmerald.exceptions import (
    EsmeraldAPIException,
    InternalServerError,
    NotAuthorized,
    NotFound,
    ServiceUnavailable,
    ValidationErrorException,
)
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.routing.router import Include
from esmerald.testclient import create_client
from esmerald.types import ExceptionHandlerMap


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (ValidationErrorException, "router"),
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling(exc_to_raise: Exception, expected_layer: str) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    with create_client(
        routes=[Gateway(path="/base", handler=ControllerWithHandler)],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
            ValidationErrorException: create_named_handler("router", ValidationErrorException),
        },
    ) as client:
        client.get("/base/test/")
        assert caller["name"] == expected_layer


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (ValidationErrorException, "router"),
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling_with_include(exc_to_raise: Exception, expected_layer: str) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    with create_client(
        routes=[Include(routes=[Gateway(path="/base", handler=ControllerWithHandler)])],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
            ValidationErrorException: create_named_handler("router", ValidationErrorException),
        },
    ) as client:
        client.get("/base/test/")
        assert caller["name"] == expected_layer


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (ValidationErrorException, "router"),
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling_with_nested_include(
    exc_to_raise: Exception, expected_layer: str
) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    with create_client(
        routes=[
            Include(
                routes=[
                    Include(
                        routes=[
                            Include(
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(
                                                        routes=[
                                                            Include(
                                                                routes=[
                                                                    Include(
                                                                        routes=[
                                                                            Include(
                                                                                routes=[
                                                                                    Include(
                                                                                        routes=[
                                                                                            Include(
                                                                                                routes=[
                                                                                                    Include(
                                                                                                        routes=[
                                                                                                            Gateway(
                                                                                                                path="/base",
                                                                                                                handler=ControllerWithHandler,
                                                                                                            )
                                                                                                        ]
                                                                                                    )
                                                                                                ]
                                                                                            )
                                                                                        ]
                                                                                    )
                                                                                ]
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
        ],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
            ValidationErrorException: create_named_handler("router", ValidationErrorException),
        },
    ) as client:
        client.get("/base/test/")
        assert caller["name"] == expected_layer


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (ValidationErrorException, "router"),
        (NotAuthorized, "include"),
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling_with_include_exception_handler(
    exc_to_raise: Exception, expected_layer: str
) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            print(caller_name)
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    with create_client(
        routes=[
            Include(
                routes=[Gateway(path="/base", handler=ControllerWithHandler)],
                exception_handlers={NotAuthorized: create_named_handler("include", NotAuthorized)},
            )
        ],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
            ValidationErrorException: create_named_handler("router", ValidationErrorException),
        },
    ) as client:
        client.get("/base/test/")
        assert caller["name"] == expected_layer


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (ValidationErrorException, "router"),
        (NotAuthorized, "include"),
        (EsmeraldAPIException, "gateway"),
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling_with_gateway_exception_handler(
    exc_to_raise: Exception, expected_layer: str
) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    with create_client(
        routes=[
            Include(
                routes=[
                    Gateway(
                        path="/base",
                        handler=ControllerWithHandler,
                        exception_handlers={
                            EsmeraldAPIException: create_named_handler(
                                "gateway", EsmeraldAPIException
                            ),
                        },
                    )
                ],
                exception_handlers={NotAuthorized: create_named_handler("include", NotAuthorized)},
            )
        ],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
            ValidationErrorException: create_named_handler("router", ValidationErrorException),
        },
    ) as client:
        client.get("/base/test/")
        assert caller["name"] == expected_layer


@pytest.mark.parametrize(
    ["exc_to_raise", "expected_layer"],
    [
        (InternalServerError, "apiview"),
        (ServiceUnavailable, "handler"),
        (NotFound, "handler"),
    ],
)
def test_exception_handling_with_child_esmerald(
    exc_to_raise: Exception, expected_layer: str
) -> None:
    caller = {"name": ""}

    def create_named_handler(
        caller_name: str, expected_exception: Type[Exception]
    ) -> "ExceptionHandlerMap":
        def handler(req: Request, exc: Exception) -> Response:
            assert isinstance(exc, expected_exception)

            caller["name"] = caller_name
            return Response(
                media_type=MediaType.JSON,
                content={},
                status_code=HTTP_400_BAD_REQUEST,
            )

        return handler

    class ControllerWithHandler(APIView):
        path = "/test"
        exception_handlers = {
            InternalServerError: create_named_handler("apiview", InternalServerError),
            ServiceUnavailable: create_named_handler("apiview", ServiceUnavailable),
        }

        @get(
            "/",
            exception_handlers={
                ServiceUnavailable: create_named_handler("handler", ServiceUnavailable),
                NotFound: create_named_handler("handler", NotFound),
            },
        )
        def my_handler(self) -> None:
            raise exc_to_raise

    child_esmerald = ChildEsmerald(routes=[Gateway(path="/base", handler=ControllerWithHandler)])

    with create_client(
        routes=[
            Include(
                routes=[Include(path="/child", app=child_esmerald)],
                exception_handlers={NotAuthorized: create_named_handler("include", NotAuthorized)},
            )
        ],
        exception_handlers={
            InternalServerError: create_named_handler("router", InternalServerError),
        },
    ) as client:
        client.get("/child/base/test/")
        assert caller["name"] == expected_layer
