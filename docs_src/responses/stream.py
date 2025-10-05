from typing import Generator

from ravyn import Ravyn, Gateway, get
from ravyn.core.datastructures import Stream


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


app = Ravyn(routes=[Gateway(handler=stream)])
