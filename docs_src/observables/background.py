from ravyn import post
from ravyn.utils.decorators import observable


@post("/upload")
@observable(send=["file_uploaded"])
async def upload_file():
    return {"message": "File uploaded successfully!"}


@observable(listen=["file_uploaded"])
async def process_file():
    print("Processing file in the background...")
