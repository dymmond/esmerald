from esmerald import Esmerald, File, Gateway, JSONResponse, UploadFile, post


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


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
