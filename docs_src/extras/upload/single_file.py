from esmerald import Body, Esmerald, Gateway, JSONResponse, UploadFile, post
from esmerald.utils.enums import EncodingType


@post("/upload")
async def upload_file(
    data: UploadFile = Body(media_type=EncodingType.MULTI_PART),
) -> JSONResponse:
    """
    Uploads a file into the system
    """
    content = await data.read()
    name = data.filename
    return JSONResponse({"filename": name, "content": content.decode()})


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
