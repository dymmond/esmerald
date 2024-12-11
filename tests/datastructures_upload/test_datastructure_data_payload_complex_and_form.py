from io import BytesIO
from pathlib import Path
from typing import Any, Dict

from esmerald import Esmerald, Form, Gateway, Request, post
from esmerald.testclient import EsmeraldTestClient


def create_dummy_file(size_in_bytes: int, filename: str = "dummy.txt"):
    file_buffer = BytesIO()
    file_buffer.write(b"0" * size_in_bytes)
    file_buffer.name = "test.txt"
    file_buffer.seek(0)
    return file_buffer


def test_upload_file_is_closed_using_complexity(tmp_path: Path):
    @post("/uploadfile/")
    async def create_upload_file(request: Request, data: Any = Form()) -> Dict[str, Any]:
        return {
            "filename": data.get("file").filename,
            "name": data.get("name"),
            "size": data.get("file").size,
        }

    app = Esmerald(routes=[Gateway(handler=create_upload_file)])
    client = EsmeraldTestClient(app)
    data = {"name": "Test"}
    response = client.post(
        "/uploadfile/",
        files={"file": create_dummy_file(size_in_bytes=2 * 1024 * 1024)},
        data=data,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {"filename": "test.txt", "name": "Test", "size": 2097152}
