from lilya import status

from esmerald.applications import ChildEsmerald
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.routing.router import Include
from esmerald.testclient import create_client


@get(status_code=status.HTTP_202_ACCEPTED)
def route_one() -> dict:
    return {"test": 1}


@get(status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_two() -> dict:
    return {"test": 2}


@get(status_code=status.HTTP_200_OK)
def route_three() -> dict:
    return {"test": 3}


@get(status_code=status.HTTP_206_PARTIAL_CONTENT)
def route_four() -> dict:
    return {"test": 4}


@get(status_code=status.HTTP_200_OK)
def route_five() -> dict:
    return {"test": 5}


def test_add_child_esmerald_app(test_client_factory) -> None:
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    with create_client(
        routes=[Gateway(handler=route_one), Include("/child", app=child_esmerald)]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_add_child_esmerald_app_within_include(test_client_factory) -> None:
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    with create_client(
        routes=[
            Gateway(handler=route_one),
            Include(routes=[Include("/child", app=child_esmerald)]),
        ]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_add_child_esmerald_app_within_nested_include_two(test_client_factory) -> None:
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    second_child = ChildEsmerald(
        routes=[
            Gateway(path="/four", handler=route_four),
            Gateway(path="/five", handler=route_five),
        ]
    )

    with create_client(
        routes=[
            Gateway(handler=route_one),
            Include(routes=[Include("/child", app=child_esmerald)]),
            Include(
                "/children",
                routes=[
                    Include(
                        routes=[
                            Include(
                                path="/nested",
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(routes=[Include(app=second_child)])
                                                ]
                                            )
                                        ]
                                    )
                                ],
                            )
                        ]
                    )
                ],
            ),
        ]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/children/nested/four")

        assert response.json() == {"test": 4}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/children/nested/five")

        assert response.json() == {"test": 5}
        assert response.status_code == status.HTTP_200_OK


def test_add_child_esmerald_app_within_nested_include(test_client_factory):
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    second_child = ChildEsmerald(
        routes=[
            Gateway(path="/four", handler=route_four),
            Gateway(path="/five", handler=route_five),
        ]
    )

    with create_client(
        routes=[
            Gateway(handler=route_one),
            Include(routes=[Include("/child", app=child_esmerald)]),
            Include(
                "/children",
                routes=[
                    Include(
                        routes=[
                            Include(
                                path="/nested",
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(routes=[Include(app=second_child)])
                                                ]
                                            )
                                        ]
                                    )
                                ],
                            )
                        ]
                    )
                ],
            ),
        ]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/children/nested/four")

        assert response.json() == {"test": 4}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/children/nested/five")

        assert response.json() == {"test": 5}
        assert response.status_code == status.HTTP_200_OK


def test_add_children_esmerald_app_within_same_nested_include(
    test_client_factory,
) -> None:
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    second_child = ChildEsmerald(
        routes=[
            Gateway(path="/four", handler=route_four),
            Gateway(path="/five", handler=route_five),
        ]
    )

    third_child = child_esmerald

    with create_client(
        routes=[
            Gateway(handler=route_one),
            Include(routes=[Include("/child", app=child_esmerald)]),
            Include(
                "/children",
                routes=[
                    Include(
                        routes=[
                            Include(
                                path="/nested",
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(routes=[Include(app=second_child)])
                                                ]
                                            )
                                        ]
                                    )
                                ],
                            ),
                            Include(
                                path="/isolated",
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[Include(routes=[Include(app=third_child)])]
                                            )
                                        ]
                                    )
                                ],
                            ),
                        ]
                    )
                ],
            ),
        ]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/children/nested/four")

        assert response.json() == {"test": 4}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/children/nested/five")

        assert response.json() == {"test": 5}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/children/isolated/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/children/isolated/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_add_children_esmerald_app_within_same_nested_include_simpler(
    test_client_factory,
) -> None:
    """
    Adds a ChildEsmerald application to the main app.
    """

    child_esmerald = ChildEsmerald(
        routes=[
            Gateway(path="/second", handler=route_two),
            Gateway(path="/third", handler=route_three),
        ]
    )

    second_child = ChildEsmerald(
        routes=[
            Gateway(path="/four", handler=route_four),
            Gateway(path="/five", handler=route_five),
        ]
    )

    third_child = child_esmerald

    with create_client(
        routes=[
            Gateway(handler=route_one),
            Include(routes=[Include("/child", app=child_esmerald)]),
            Include(
                "/apps",
                routes=[
                    Include("/clients", second_child),
                    Include("/customers", third_child),
                    Include("/isolated", child_esmerald),
                ],
            ),
        ]
    ) as client:
        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/child/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/child/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/apps/clients/four")

        assert response.json() == {"test": 4}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/apps/clients/five")

        assert response.json() == {"test": 5}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/apps/customers/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/apps/customers/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/apps/isolated/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/apps/isolated/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK
