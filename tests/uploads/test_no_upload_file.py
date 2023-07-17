from typing import Dict, Union

from esmerald import Esmerald, Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import EsmeraldTestClient


@post("/files", status_code=status.HTTP_200_OK)
async def create_file(data: Union[UploadFile, None] = File()) -> Dict[str, str]:
    if not data:
        return {"details": "No file sent"}

    file = await data.read()
    return {"size": len(file)}


@post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(data: Union[UploadFile, None] = File()) -> Dict[str, str]:
    if not data:
        return {"details": "No file sent"}
    return {"size": data.filename}


app = Esmerald(
    routes=[Gateway(handler=create_file), Gateway(handler=upload_file)], enable_openapi=True
)
client = EsmeraldTestClient(app)


def test_post_form_no_body():
    response = client.post("/files")
    assert response.status_code == 200, response.text
    assert response.json() == {"details": "No file sent"}


def test_post_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/files", files={"file": file})
    assert response.status_code == 200, response.text
    assert response.json() == {"size": 14}


def test_post_upload_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/upload", files={"file": file})

    assert response.status_code == 200, response.text
    assert response.json() == {"size": "test.txt"}


def test_openapi_schema(test_client_factory):
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Esmerald",
            "summary": "Esmerald application",
            "description": "test_client",
            "contact": {"name": "admin", "email": "admin@myapp.com"},
            "version": client.app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/files": {
                "post": {
                    "summary": "Create File",
                    "operationId": "create_file_files_post",
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "anyOf": [
                                        {"type": "string", "format": "binary"},
                                        {"type": "null"},
                                    ],
                                    "title": "Optional",
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
                                }
                            },
                        },
                    },
                    "deprecated": False,
                }
            },
            "/upload": {
                "post": {
                    "summary": "Upload File",
                    "operationId": "upload_file_upload_post",
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "anyOf": [
                                        {"type": "string", "format": "binary"},
                                        {"type": "null"},
                                    ],
                                    "title": "Optional",
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
                                }
                            },
                        },
                    },
                    "deprecated": False,
                }
            },
        },
        "components": {
            "schemas": {
                "HTTPValidationError": {
                    "properties": {
                        "detail": {
                            "items": {"$ref": "#/components/schemas/ValidationError"},
                            "type": "array",
                            "title": "Detail",
                        }
                    },
                    "type": "object",
                    "title": "HTTPValidationError",
                },
                "ValidationError": {
                    "properties": {
                        "loc": {
                            "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                            "type": "array",
                            "title": "Location",
                        },
                        "msg": {"type": "string", "title": "Message"},
                        "type": {"type": "string", "title": "Error Type"},
                    },
                    "type": "object",
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationError",
                },
            }
        },
    }
