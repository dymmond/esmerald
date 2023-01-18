from routing.gateways import Gateway

from esmerald import Body, Esmerald, JSONResponse, UploadFile, post
from esmerald.enums import EncodingType, MediaType


@post("/upload", media_type=MediaType.TEXT)
async def upload_file(data: UploadFile = Body(media_type=EncodingType.MULTI_PART)) -> JSONResponse:
    """
    Uploads a file into the system
    """
    content = await data.read()
    name = data.filename
    return JSONResponse({"filename": name, "content": content.decode()})


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
