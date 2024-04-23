from typing import Any, Type, Union

import pytest
from lilya.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from pydantic import BaseModel

from esmerald.enums import HttpMethod, MediaType
from esmerald.responses import Response
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.handlers import delete, get, patch, post, put, websocket
from esmerald.routing.router import Include
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket
from tests.models import Individual, IndividualFactory


class MyView(APIView):
    @get("/event")
    async def event(self) -> None:
        """"""

    @get("/events")
    async def events(self) -> None:
        """"""


def test_can_generate_views(test_client_factory):
    with create_client(routes=[Gateway(handler=MyView)], enable_openapi=False) as client:
        assert len(client.app.routes) == 2


@pytest.mark.parametrize(
    "http_verb, http_method, expected_status_code, return_value, return_annotation",
    [
        (
            get,
            HttpMethod.GET,
            HTTP_200_OK,
            Response(
                content=IndividualFactory.build(),
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            ),
            Response[Individual],
        ),
        (get, HttpMethod.GET, HTTP_200_OK, IndividualFactory.build(), Individual),
        (post, HttpMethod.POST, HTTP_201_CREATED, IndividualFactory.build(), Individual),
        (put, HttpMethod.PUT, HTTP_200_OK, IndividualFactory.build(), Individual),
        (patch, HttpMethod.PATCH, HTTP_200_OK, IndividualFactory.build(), Individual),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT, None, None),
    ],
)
def test_controller_http_method(
    http_verb: Union[Type[get], Type[post], Type[put], Type[patch], Type[delete]],
    http_method: HttpMethod,
    expected_status_code: int,
    return_value: Any,
    return_annotation: Any,
) -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @http_verb(path="/")
        def test_method(self) -> return_annotation:  # type: ignore[valid-type]
            return return_value  # type: ignore[no-any-return]

    with create_client(routes=[Gateway(path="/", handler=MyAPIView)]) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code
        if return_value:
            assert (
                response.json() == return_value.model_dump()
                if isinstance(return_value, BaseModel)
                else return_value
            )


@pytest.mark.parametrize(
    "http_verb, http_method, expected_status_code, return_value, return_annotation",
    [
        (
            get,
            HttpMethod.GET,
            HTTP_200_OK,
            Response(
                content=IndividualFactory.build(),
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            ),
            Response[Individual],
        ),
        (get, HttpMethod.GET, HTTP_200_OK, IndividualFactory.build(), Individual),
        (post, HttpMethod.POST, HTTP_201_CREATED, IndividualFactory.build(), Individual),
        (put, HttpMethod.PUT, HTTP_200_OK, IndividualFactory.build(), Individual),
        (patch, HttpMethod.PATCH, HTTP_200_OK, IndividualFactory.build(), Individual),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT, None, None),
    ],
)
def test_controller_http_method_with_include(
    http_verb: Union[Type[get], Type[post], Type[put], Type[patch], Type[delete]],
    http_method: HttpMethod,
    expected_status_code: int,
    return_value: Any,
    return_annotation: Any,
) -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @http_verb(path="/")
        def test_method(self) -> return_annotation:  # type: ignore[valid-type]
            return return_value  # type: ignore[no-any-return]

    with create_client(
        routes=[Include(path="/", routes=[Gateway(path="/", handler=MyAPIView)])]
    ) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code
        if return_value:
            assert (
                response.json() == return_value.model_dump()
                if isinstance(return_value, BaseModel)
                else return_value
            )


@pytest.mark.parametrize(
    "http_verb, http_method, expected_status_code, return_value, return_annotation",
    [
        (
            get,
            HttpMethod.GET,
            HTTP_200_OK,
            Response(
                content=IndividualFactory.build(),
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            ),
            Response[Individual],
        ),
        (get, HttpMethod.GET, HTTP_200_OK, IndividualFactory.build(), Individual),
        (post, HttpMethod.POST, HTTP_201_CREATED, IndividualFactory.build(), Individual),
        (put, HttpMethod.PUT, HTTP_200_OK, IndividualFactory.build(), Individual),
        (patch, HttpMethod.PATCH, HTTP_200_OK, IndividualFactory.build(), Individual),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT, None, None),
    ],
)
def test_controller_http_method_with_nested_include(
    http_verb: Union[Type[get], Type[post], Type[put], Type[patch], Type[delete]],
    http_method: HttpMethod,
    expected_status_code: int,
    return_value: Any,
    return_annotation: Any,
) -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @http_verb(path="/")
        def test_method(self) -> return_annotation:  # type: ignore[valid-type]
            return return_value  # type: ignore[no-any-return]

    with create_client(
        routes=[
            Include(
                path="/",
                routes=[Include(path="/", routes=[Gateway(path="/", handler=MyAPIView)])],
            )
        ]
    ) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code
        if return_value:
            assert (
                response.json() == return_value.model_dump()
                if isinstance(return_value, BaseModel)
                else return_value
            )


@pytest.mark.parametrize(
    "http_verb, http_method, expected_status_code, return_value, return_annotation",
    [
        (
            get,
            HttpMethod.GET,
            HTTP_200_OK,
            Response(
                content=IndividualFactory.build(),
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            ),
            Response[Individual],
        ),
        (get, HttpMethod.GET, HTTP_200_OK, IndividualFactory.build(), Individual),
        (post, HttpMethod.POST, HTTP_201_CREATED, IndividualFactory.build(), Individual),
        (put, HttpMethod.PUT, HTTP_200_OK, IndividualFactory.build(), Individual),
        (patch, HttpMethod.PATCH, HTTP_200_OK, IndividualFactory.build(), Individual),
        (delete, HttpMethod.DELETE, HTTP_204_NO_CONTENT, None, None),
    ],
)
def test_controller_http_method_with_super_nested_include(
    http_verb: Union[Type[get], Type[post], Type[put], Type[patch], Type[delete]],
    http_method: HttpMethod,
    expected_status_code: int,
    return_value: Any,
    return_annotation: Any,
) -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @http_verb(path="/")
        def test_method(self) -> return_annotation:  # type: ignore[valid-type]
            return return_value  # type: ignore[no-any-return]

    with create_client(
        routes=[
            Include(
                path="/",
                routes=[
                    Include(
                        path="/",
                        routes=[
                            Include(
                                path="/",
                                routes=[
                                    Include(
                                        path="/",
                                        routes=[
                                            Include(
                                                path="/",
                                                routes=[
                                                    Include(
                                                        path="/",
                                                        routes=[
                                                            Include(
                                                                path="/",
                                                                routes=[
                                                                    Include(
                                                                        path="/",
                                                                        routes=[
                                                                            Include(
                                                                                path="/",
                                                                                routes=[
                                                                                    Include(
                                                                                        path="/",
                                                                                        routes=[
                                                                                            Include(
                                                                                                path="/",
                                                                                                routes=[
                                                                                                    Gateway(
                                                                                                        path="/",
                                                                                                        handler=MyAPIView,
                                                                                                    )
                                                                                                ],
                                                                                            )
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ]
    ) as client:
        response = client.request(http_method, test_path)
        assert response.status_code == expected_status_code
        if return_value:
            assert (
                response.json() == return_value.model_dump()
                if isinstance(return_value, BaseModel)
                else return_value
            )


def test_controller_with_websocket_handler() -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @get(path="/")
        def get_person(self) -> Individual:
            """ """

        @websocket(path="/socket")
        async def ws(self, socket: WebSocket) -> None:
            await socket.accept()
            await socket.send_json({"data": "123"})
            await socket.close()

    client = create_client(routes=[Gateway(path="/", handler=MyAPIView)])

    with client.websocket_connect(test_path + "/socket") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data


def test_controller_with_include_websocket_handler() -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @get(path="/")
        def get_person(self) -> Individual:
            """ """

        @websocket(path="/socket")
        async def ws(self, socket: WebSocket) -> None:
            await socket.accept()
            await socket.send_json({"data": "123"})
            await socket.close()

    client = create_client(
        routes=[Include(path="/", routes=[Gateway(path="/", handler=MyAPIView)])]
    )

    with client.websocket_connect(test_path + "/socket") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data


def test_controller_with_nested_include_websocket_handler() -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @get(path="/")
        def get_person(self) -> Individual:
            """ """

        @websocket(path="/socket")
        async def ws(self, socket: WebSocket) -> None:
            await socket.accept()
            await socket.send_json({"data": "123"})
            await socket.close()

    client = create_client(
        routes=[
            Include(
                path="/",
                routes=[Include(path="/", routes=[Gateway(path="/", handler=MyAPIView)])],
            )
        ]
    )

    with client.websocket_connect(test_path + "/socket") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data


def test_controller_with_super_nested_include_websocket_handler() -> None:
    test_path = "/person"

    class MyAPIView(APIView):
        path = test_path

        @get(path="/")
        def get_person(self) -> Individual:
            """ """

        @websocket(path="/socket")
        async def ws(self, socket: WebSocket) -> None:
            await socket.accept()
            await socket.send_json({"data": "123"})
            await socket.close()

    client = create_client(
        routes=[
            Include(
                path="/",
                routes=[
                    Include(
                        path="/",
                        routes=[
                            Include(
                                path="/",
                                routes=[
                                    Include(
                                        path="/",
                                        routes=[
                                            Include(
                                                path="/",
                                                routes=[
                                                    Include(
                                                        path="/",
                                                        routes=[
                                                            Include(
                                                                path="/",
                                                                routes=[
                                                                    Include(
                                                                        path="/",
                                                                        routes=[
                                                                            Include(
                                                                                path="/",
                                                                                routes=[
                                                                                    Include(
                                                                                        path="/",
                                                                                        routes=[
                                                                                            Include(
                                                                                                path="/",
                                                                                                routes=[
                                                                                                    Include(
                                                                                                        path="/",
                                                                                                        routes=[
                                                                                                            Gateway(
                                                                                                                path="/",
                                                                                                                handler=MyAPIView,
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            )
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        ]
    )

    with client.websocket_connect(test_path + "/socket") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data


def test_api_view_path_parameter():
    class MyAPIView(APIView):
        path = "/customer/{name}"

        @get(path="/")
        def home(self, name: str) -> str:  # type: ignore[valid-type]
            return name

        @get(path="/test")
        def home_test(self, name: str) -> str:  # type: ignore[valid-type]
            return f"Test {name}"

        @get(path="/test/{param}")
        def param_test(self, name: str, param: str) -> str:  # type: ignore[valid-type]
            return f"Test {name} {param}"

    with create_client(routes=[Gateway(handler=MyAPIView)]) as client:
        response = client.get("/customer/esmerald")
        assert response.status_code == HTTP_200_OK
        assert response.json() == "esmerald"

        response = client.get("/customer/esmerald/test")
        assert response.status_code == HTTP_200_OK
        assert response.json() == "Test esmerald"

        response = client.get("/customer/esmerald/test/param")
        assert response.status_code == HTTP_200_OK
        assert response.json() == "Test esmerald param"


def test_controller_with_websocket_gateway() -> None:
    class MyAPIView(APIView):
        path = "/"

        @websocket(path="/socket")
        async def ws(self, socket: WebSocket) -> None:
            await socket.accept()
            await socket.send_json({"data": "123"})
            await socket.close()

    client = create_client(routes=[WebSocketGateway(handler=MyAPIView)])

    with client.websocket_connect("/socket") as ws:
        ws.send_json({"data": "123"})
        data = ws.receive_json()
        assert data
