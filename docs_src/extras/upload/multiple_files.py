from routing.gateways import Gateway

from esmerald import Body, Esmerald, JSONResponse, UploadFile, post
from esmerald.enums import EncodingType, MediaType
from esmerald.parsers import ArbitraryBaseModel


class UserFormData(ArbitraryBaseModel):
    """
    Using ArbitraryBaseModel is the same as using

    Example:
        from pydantic import BaseConfig, BaseModel


        class MyClass(BaseModel):
            field_one: str
            field_two: int

            class Config(BaseConfig):
                arbitrary_types_allowed = True

    """

    curriculum: UploadFile
    projects: UploadFile
    certifications: UploadFile


@post("/upload", media_type=MediaType.TEXT)
async def upload_file(
    data: UserFormData = Body(media_type=EncodingType.MULTI_PART),
) -> JSONResponse:
    """
    Uploads a file into the system
    """
    curriculum = await data.curriculum.read()
    projects = await data.projects.read()
    certifications = await data.certifications.read()

    return JSONResponse(
        {
            "curriculum": curriculum.decode(),
            "projects": projects.decode(),
            "certifications": certifications.decode(),
        }
    )


app = Esmerald(routes=[Gateway(handler=upload_file, name="upload-file")])
