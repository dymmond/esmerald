from ravyn import Body, Ravyn, Gateway, JSONResponse, UploadFile, post
from ravyn.utils.enums import EncodingType


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


app = Ravyn(routes=[Gateway(handler=upload_file, name="upload-file")])
