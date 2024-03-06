import os
import pathlib
from typing import Any

import pytest
from pydantic import ValidationError

from esmerald.config import StaticFilesConfig

# from esmerald.requests import Request
# from esmerald.routing.router import Include
from esmerald.testclient import create_client

# from lilya.middleware import DefineMiddleware

# from starlette.middleware.base import BaseHTTPMiddleware


def test_staticfiles(tmpdir: str) -> None:
    path = tmpdir.join("test.txt")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"


def test_staticfiles_starlette(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "example.txt")
    with open(path, "w") as file:
        file.write("<file content>")

    static_files_config = StaticFilesConfig(path="/", directory=tmpdir)

    with create_client(routes=[], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "<file content>"


def test_staticfiles_with_pathlib(tmpdir, test_client_factory):
    base_dir = pathlib.Path(tmpdir)
    path = base_dir / "example.txt"
    with open(path, "w") as file:
        file.write("<file content>")

    static_files_config = StaticFilesConfig(path="/", directory=base_dir)
    with create_client(routes=[], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "<file content>"


# def test_staticfiles_head_with_middleware(tmpdir, test_client_factory):
#     """
#     see https://github.com/encode/starlette/pull/935
#     """
#     path = os.path.join(tmpdir, "example.txt")
#     with open(path, "w") as file:
#         file.write("x" * 100)

#     async def does_nothing_middleware(request: Request, call_next):
#         response = await call_next(request)
#         return response

#     static_files_config = StaticFilesConfig(path="/", directory=tmpdir)
#     routes = [Include("/static", app=static_files_config.to_app(), name="static")]
#     middleware = [DefineMiddleware(BaseHTTPMiddleware, dispatch=does_nothing_middleware)]

#     with create_client(
#         routes=routes, static_files_config=static_files_config, middleware=middleware
#     ) as client:
#         response = client.head("/static/example.txt")
#         assert response.status_code == 200
#         assert response.headers.get("content-length") == "100"


def test_staticfiles_html(tmpdir: Any) -> None:
    path = tmpdir.join("index.html")
    path.write("content")
    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir, html=True)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert response.text == "content"


def test_staticfiles_with_package(test_client_factory):
    static_files_config = StaticFilesConfig(path="/", packages=["tests"], html=True)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/example.txt")
        assert response.status_code == 200
        assert response.text == "123\n"


def test_staticfiles_for_slash_path(tmpdir: Any) -> None:
    path = tmpdir.join("text.txt")
    path.write("content")

    static_files_config = StaticFilesConfig(path="/", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/text.txt")
        assert response.status_code == 200
        assert response.text == "content"


def test_config_validation(tmpdir: Any) -> None:
    path = tmpdir.join("text.txt")
    path.write("content")

    with pytest.raises(ValidationError):
        StaticFilesConfig(path="", directory=tmpdir)

    with pytest.raises(ValidationError):
        StaticFilesConfig(path="/{param:int}", directory=tmpdir)


def test_multiple_configs(tmpdir: Any) -> None:
    root1 = tmpdir.mkdir("1")
    root2 = tmpdir.mkdir("2")
    path1 = root1.join("test.txt")
    path1.write("content1")
    path2 = root2.join("test.txt")
    path2.write("content2")

    static_files_config = [
        StaticFilesConfig(path="/1", directory=root1),
        StaticFilesConfig(path="/2", directory=root2),
    ]
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/1/test.txt")
        assert response.status_code == 200
        assert response.text == "content1"

        response = client.get("/2/test.txt")
        assert response.status_code == 200
        assert response.text == "content2"


def test_static_substring_of_self(tmpdir: Any) -> None:
    path = tmpdir.mkdir("static_part").mkdir("static")
    path = path.join("test.txt")
    path.write("content")

    static_files_config = StaticFilesConfig(path="/static", directory=tmpdir)
    with create_client([], static_files_config=static_files_config) as client:
        response = client.get("/static/static_part/static/test.txt")
        assert response.status_code == 200
        assert response.text == "content"
