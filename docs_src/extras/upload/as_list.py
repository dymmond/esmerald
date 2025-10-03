from typing import Dict, List

from ravyn import Body, Ravyn, Gateway, UploadFile, post
from ravyn.utils.enums import EncodingType


@post("/upload")
async def upload_file(
    data: List[UploadFile] = Body(media_type=EncodingType.MULTI_PART),
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
