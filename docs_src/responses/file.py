from ravyn import Ravyn, Gateway, get
from ravyn.core.datastructures import File


@get(
    path="/download",
)
def download() -> File:
    return File(
        path="/path/to/file",
        filename="download.csv",
    )


app = Ravyn(routes=[Gateway(handler=download)])
