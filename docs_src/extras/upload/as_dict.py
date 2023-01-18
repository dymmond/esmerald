from typing import Dict

from routing.gateways import Gateway

from esmerald import Body, Esmerald, UploadFile, post
from esmerald.enums import EncodingType, MediaType


@post("/upload", media_type=MediaType.TEXT)
async def upload_file(
    data: Dict[str, UploadFile] = Body(media_type=EncodingType.MULTI_PART),
) -> Dict[str, str]:
    """
    Uploads a file into the system
    """
    contents = {}
    for name, file in data.items():
        content = await file.read()
        contents[name] = content.decode()

    return contents


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
