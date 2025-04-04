from esmerald import Esmerald, Gateway, get
from esmerald.core.datastructures import File


@get(
    path="/download",
)
def download() -> File:
    return File(
        path="/path/to/file",
        filename="download.csv",
    )


app = Esmerald(routes=[Gateway(handler=download)])
