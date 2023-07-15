from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import pytest
from pydantic import BaseModel

from esmerald import Body, Esmerald, Gateway, UploadFile, post
from esmerald.enums import EncodingType
from esmerald.testclient import EsmeraldTestClient, create_client


class FormData(BaseModel):
    name: UploadFile
    age: UploadFile
    programmer: UploadFile

    model_config = {"arbitrary_types_allowed": True}


class Form(BaseModel):
    name: str
    age: Optional[int] = None
    programmer: bool


@pytest.mark.parametrize("t_type", [Dict[str, UploadFile], List[UploadFile], UploadFile])
def xtest_request_body_multi_part(t_type: Type[Any]) -> None:
    body = Body(media_type=EncodingType.MULTI_PART)

    test_path = "/test"
    data = Form(name="Moishe Zuchmir", programmer=True).model_dump()

    @post(path=test_path)
    def test_method(data: t_type = body) -> None:  # type: ignore
        assert data

    with create_client(routes=[Gateway(handler=test_method)]) as client:
        breakpoint()
        response = client.post(test_path, files=data)
        assert response.status_code == 201


def test_upload_file_is_closed(tmp_path: Path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    testing_file_store: List[UploadFile] = []

    @post("/uploadfile/")
    async def create_upload_file(
        data: UploadFile = Body(media_type=EncodingType.MULTI_PART),
    ) -> Dict[str, Any]:
        testing_file_store.append(file)
        return {"filename": data.filename}

    app = Esmerald(routes=[Gateway(handler=create_upload_file)])
    client = EsmeraldTestClient(app)
    with path.open("rb") as file:
        response = client.post("/uploadfile/", files={"file": file})
    assert response.status_code == 201, response.text
    assert response.json() == {"filename": "test.txt"}

    assert testing_file_store
    assert testing_file_store[0].closed
