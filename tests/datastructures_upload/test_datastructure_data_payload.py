from pathlib import Path
from typing import Any, Dict, List

from ravyn import Body, Gateway, Ravyn, UploadFile, post
from ravyn.testclient import RavynTestClient
from ravyn.utils.enums import EncodingType


def test_upload_file_is_closed(tmp_path: Path):
    path = tmp_path / "test.txt"
    path.write_bytes(b"<file content>")

    testing_file_store: List[UploadFile] = []

    @post("/uploadfile/")
    async def create_upload_file(
        payload: UploadFile = Body(media_type=EncodingType.MULTI_PART),
    ) -> Dict[str, Any]:
        testing_file_store.append(file)
        return {"filename": payload.filename}

    app = Ravyn(routes=[Gateway(handler=create_upload_file)])
    client = RavynTestClient(app)
    with path.open("rb") as file:
        response = client.post("/uploadfile", files={"file": file})
    assert response.status_code == 201, response.text
    assert response.json() == {"filename": "test.txt"}

    assert testing_file_store
    assert testing_file_store[0].closed
