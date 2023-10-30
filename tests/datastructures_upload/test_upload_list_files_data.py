from typing import Any, Dict, List, Union

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import EsmeraldTestClient, create_client


class MultipleFile(BaseModel):
    one: Union[UploadFile, Any]
    two: Union[UploadFile, Any]

    model_config = {"arbitrary_types_allowed": True}


@post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(data: List[Union[UploadFile, None]] = File()) -> Dict[str, str]:
    names = []
    for file in data:
        names.append(file.filename)
    return {"names": names}


@post("/upload-multiple", status_code=status.HTTP_200_OK)
async def upload_list_multiple_file(
    data: List[Union[UploadFile, None]] = File()
) -> Dict[str, str]:
    names = []
    for file in data:
        names.append(file.filename)

    total = len(data)
    return {"names": names, "total": total}


app = Esmerald(
    routes=[
        Gateway(handler=upload_file),
        Gateway(handler=upload_list_multiple_file),
    ]
)
client = EsmeraldTestClient(app)


def test_post_upload_file(test_client_factory, tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/upload", files={"file": file})

    assert response.status_code == 200, response.text
    assert response.json() == {"names": ["test.txt"]}


def test_post_upload_list_multiple_file(test_client_factory, tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/upload-multiple", files={"file": file, "file2": file})

    assert response.status_code == 200, response.text
    assert response.json() == {"names": ["test.txt", "test.txt"], "total": 2}


def test_openapi_schema(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=upload_file),
            Gateway(handler=upload_list_multiple_file),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200, response.text

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Esmerald",
                "summary": "Esmerald application",
                "description": "Highly scalable, performant, easy to learn and for every application.",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": client.app.version,
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/upload": {
                    "post": {
                        "summary": "Upload File",
                        "operationId": "upload_file_upload_post",
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Body_upload_file_upload_post"
                                    }
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            },
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/HTTPValidationError"
                                        }
                                    }
                                },
                            },
                        },
                        "deprecated": False,
                    }
                },
                "/upload-multiple": {
                    "post": {
                        "summary": "Upload List Multiple File",
                        "operationId": "upload_list_multiple_file_upload_multiple_post",
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Body_upload_list_multiple_file_upload_multiple_post"
                                    }
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            },
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/HTTPValidationError"
                                        }
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
                    "Body_upload_file_upload_post": {
                        "properties": {
                            "files": {
                                "items": {
                                    "anyOf": [
                                        {"type": "string", "format": "binary"},
                                        {"type": "null"},
                                    ]
                                },
                                "type": "array",
                                "title": "Body_upload_file_upload_post",
                            }
                        },
                        "type": "object",
                        "required": ["files"],
                        "title": "Body_upload_file_upload_post",
                    },
                    "Body_upload_list_multiple_file_upload_multiple_post": {
                        "properties": {
                            "files": {
                                "items": {
                                    "anyOf": [
                                        {"type": "string", "format": "binary"},
                                        {"type": "null"},
                                    ]
                                },
                                "type": "array",
                                "title": "Body_upload_list_multiple_file_upload_multiple_post",
                            }
                        },
                        "type": "object",
                        "required": ["files"],
                        "title": "Body_upload_list_multiple_file_upload_multiple_post",
                    },
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
