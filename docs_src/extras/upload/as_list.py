from typing import Dict, List

from routing.gateways import Gateway

from esmerald import Body, Esmerald, UploadFile, post
from esmerald.enums import EncodingType, MediaType


@post("/upload", media_type=MediaType.TEXT)
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


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
