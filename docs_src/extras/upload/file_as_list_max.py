from typing import Dict, List

from ravyn import Ravyn, File, Gateway, UploadFile, post


@post("/upload")
async def upload_file(
    data: List[UploadFile] = File(max_length=3),
) -> Dict[str, str]:
    """
    Uploads a file into the system
    """
    contents = {}
    for file in data:
        content = await file.read()
        contents[file.filename] = content.decode()

    return contents


app = Ravyn(routes=[Gateway(handler=upload_file, name="upload-file")])
