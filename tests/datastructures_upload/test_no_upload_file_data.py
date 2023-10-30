from typing import Dict, Union

from esmerald import Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import create_client


@post("/files", status_code=status.HTTP_200_OK)
async def create_file(data: Union[UploadFile, None] = File()) -> Dict[str, str]:
    if not data:
        return {"details": "No file sent"}

    file = await data.read()
    return {"size": len(file)}


@post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(data: Union[UploadFile, None] = File()) -> Dict[str, str]:
    return {"size": data.filename}


def test_post_form_no_body():
    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)], enable_openapi=True
    ) as client:
        response = client.post("/files")
        assert response.status_code == 200, response.text
        assert response.json() == {"details": "No file sent"}


def test_post_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)], enable_openapi=True
    ) as client:
        with path.open("rb") as file:
            response = client.post("/files", files={"file": file})
        assert response.status_code == 200, response.text
        assert response.json() == {"size": 14}


def test_post_upload_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    with create_client(
        routes=[Gateway(handler=create_file), Gateway(handler=upload_file)], enable_openapi=True
    ) as client:
        with path.open("rb") as file:
            response = client.post("/upload", files={"file": file})

        assert response.status_code == 200, response.text
        assert response.json() == {"size": "test.txt"}
