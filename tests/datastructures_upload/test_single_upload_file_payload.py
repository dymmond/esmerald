from typing import Dict

from esmerald import Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import create_client


@post("/files", status_code=status.HTTP_200_OK)
async def create_file(payload: UploadFile = File()) -> Dict[str, str]:
    file = await payload.read()
    return {"size": len(file)}


@post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(payload: UploadFile = File()) -> Dict[str, str]:
    return {"size": payload.filename}


def test_post_file(test_client_factory, tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)],
        enable_openapi=True,
    ) as client:
        with path.open("rb") as file:
            response = client.post("/files", files={"file": file})
        assert response.status_code == 200, response.text
        assert response.json() == {"size": 14}


def test_post_upload_file(test_client_factory, tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)],
        enable_openapi=True,
    ) as client:
        with path.open("rb") as file:
            response = client.post("/upload", files={"file": file})

        assert response.status_code == 200, response.text
        assert response.json() == {"size": "test.txt"}


def test_openapi_schema(test_client_factory):
    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)],
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
                "/files": {
                    "post": {
                        "summary": "Create File",
                        "operationId": "create_file_files_post",
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Body_create_file_files_post"
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
            },
            "components": {
                "schemas": {
                    "Body_create_file_files_post": {
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "title": "Body_create_file_files_post",
                            }
                        },
                        "type": "object",
                        "required": ["file"],
                        "title": "Body_create_file_files_post",
                    },
                    "Body_upload_file_upload_post": {
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "title": "Body_upload_file_upload_post",
                            }
                        },
                        "type": "object",
                        "required": ["file"],
                        "title": "Body_upload_file_upload_post",
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
