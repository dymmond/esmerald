from flask import Flask, request
from markupsafe import escape

from esmerald import Esmerald, Gateway, Include, Request, get
from esmerald.middleware import WSGIMiddleware
from esmerald.testclient import create_client

flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from Flask!"


@get("/home/{name:str}")
async def home(request: Request) -> dict:
    name = request.path_params["name"]
    return {"name": name}


def test_serve_flask_via_esmerald(test_client_factory):
    routes = [
        Gateway(handler=home),
        Include("/flask", WSGIMiddleware(flask_app)),
    ]

    with create_client(routes=routes, enable_openapi=False) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_flask_via_nested_include(test_client_factory):
    routes = [
        Gateway(handler=home),
        Include(
            routes=[
                Include("/flask", WSGIMiddleware(flask_app)),
            ]
        ),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_flask_via_deep_nested_include(test_client_factory):
    routes = [
        Gateway(handler=home),
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
                                                            "/flask",
                                                            WSGIMiddleware(flask_app),
                                                        ),
                                                    ]
                                                ),
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
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


second_flask_app = Flask(__name__)


@second_flask_app.route("/")
def second_flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from Flask!"


def test_serve_more_than_one_flask_app_via_esmerald(test_client_factory):
    routes = [
        Gateway(handler=home),
        Include("/flask", WSGIMiddleware(flask_app)),
        Include("/second/flask", WSGIMiddleware(second_flask_app)),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_more_than_one_flask_app_via_esmerald_two(test_client_factory):
    routes = [
        Gateway(handler=home),
        Include("/flask", WSGIMiddleware(flask_app)),
        Include("/second/flask", WSGIMiddleware(second_flask_app)),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_more_than_one_flask_app_via_nested_include(test_client_factory):
    routes = [
        Gateway(handler=home),
        Include(
            routes=[
                Include(
                    "/internal",
                    routes=[
                        Include(
                            routes=[
                                Include("/flask", WSGIMiddleware(flask_app)),
                            ]
                        )
                    ],
                ),
                Include(
                    routes=[
                        Include(
                            routes=[
                                Include(
                                    "/external",
                                    routes=[
                                        Include(
                                            "/second/flask",
                                            WSGIMiddleware(second_flask_app),
                                        ),
                                    ],
                                )
                            ]
                        )
                    ]
                ),
            ]
        ),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/internal/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/external/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_routes_inder_main_path(test_client_factory):
    routes = [
        Include(
            path="/",
            routes=[
                Gateway(handler=home),
                Include("/flask", WSGIMiddleware(flask_app)),
                Include("/second/flask", WSGIMiddleware(second_flask_app)),
            ],
        )
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_routes_inder_main_path_with_different_names(test_client_factory):
    routes = [
        Include(
            path="/api/v1",
            routes=[
                Gateway(handler=home),
                Include(
                    "/ext/v2",
                    routes=[
                        Include("/flask", WSGIMiddleware(flask_app)),
                        Include("/second/flask", WSGIMiddleware(second_flask_app)),
                    ],
                ),
            ],
        )
    ]

    with create_client(routes=routes) as client:
        response = client.get("/api/v1/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/api/v1/ext/v2/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/api/v1/ext/v2/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_under_another_esmerald_app(test_client_factory):
    esmerald_app = Esmerald(
        routes=[
            Gateway(handler=home),
            Include("/flask", WSGIMiddleware(flask_app)),
            Include("/second/flask", WSGIMiddleware(second_flask_app)),
        ]
    )

    routes = [
        Include("/esmerald", esmerald_app),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/esmerald/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/esmerald/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/esmerald/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"


def test_serve_under_another_esmerald_app_two(test_client_factory):
    esmerald_app = Esmerald(
        routes=[
            Gateway(handler=home),
            Include("/flask", WSGIMiddleware(flask_app)),
            Include("/second/flask", WSGIMiddleware(second_flask_app)),
        ]
    )

    routes = [
        Gateway(handler=home),
        Include("/esmerald", esmerald_app),
        Gateway("/test", handler=home),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/test/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/esmerald/home/esmerald")
        assert response.status_code == 200
        assert response.json() == {"name": "esmerald"}

        response = client.get("/esmerald/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"

        response = client.get("/esmerald/second/flask")
        assert response.status_code == 200
        assert response.text == "Hello, Esmerald from Flask!"
