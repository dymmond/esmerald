from typing import Any, Dict, List, Union

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, UploadFile, post, status
from esmerald.params import File
from esmerald.testclient import EsmeraldTestClient


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


@post("/upload-dict-multiple", status_code=status.HTTP_200_OK)
async def upload_dict_multiple_file(data: MultipleFile = File()) -> Dict[str, str]:
    return {"names": [], "total": 2}


app = Esmerald(
    routes=[
        Gateway(handler=upload_file),
        Gateway(handler=upload_list_multiple_file),
    ]
)
client = EsmeraldTestClient(app)


def test_post_upload_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/upload", files={"file": file})

    assert response.status_code == 200, response.text
    assert response.json() == {"names": ["test.txt"]}


def test_post_upload_list_multiple_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/upload-multiple", files={"file": file, "file2": file})

    assert response.status_code == 200, response.text
    assert response.json() == {"names": ["test.txt", "test.txt"], "total": 2}
