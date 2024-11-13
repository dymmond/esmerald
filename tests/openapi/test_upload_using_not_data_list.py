from typing import Dict, List

from esmerald import Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import create_client


@post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(upload: List[UploadFile] = File()) -> Dict[str, str]:
    names = []
    for file in upload:
        names.append(file.filename)
    return {"names": names}


def test_openapi_schema(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=upload_file),
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
                        "description": "",
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
                }
            },
            "components": {
                "schemas": {
                    "Body_upload_file_upload_post": {
                        "properties": {
                            "files": {
                                "items": {"type": "string", "format": "binary"},
                                "type": "array",
                                "title": "Body_upload_file_upload_post",
                            }
                        },
                        "type": "object",
                        "required": ["files"],
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
