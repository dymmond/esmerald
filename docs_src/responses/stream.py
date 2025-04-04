from typing import Generator

from esmerald import Esmerald, Gateway, get
from esmerald.core.datastructures import Stream


def my_generator() -> Generator[str, None, None]:
    count = 0
    while True:
        count += 1
        yield str(count)


@get(
    path="/stream",
)
def stream() -> Stream:
    return Stream(
        iterator=my_generator(),
    )


app = Esmerald(routes=[Gateway(handler=stream)])
