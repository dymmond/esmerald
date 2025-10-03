from ravyn import Ravyn, File, Gateway, JSONResponse, UploadFile, post


@post("/upload")
async def upload_file(
    data: UploadFile = File(),
) -> JSONResponse:
    """
    Uploads a file into the system
    """
    content = await data.read()
    name = data.filename
    return JSONResponse({"filename": name, "content": content.decode()})


app = Ravyn(routes=[Gateway(handler=upload_file, name="upload-file")])
