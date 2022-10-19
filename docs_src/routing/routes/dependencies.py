from esmerald import Esmerald, Gateway, get


def first_dependency() -> bool:
    return True


async def second_dependency() -> str:
    return "Second dependency"


async def third_dependency() -> dict:
    return {"third": "dependency"}


@get(path="/home", dependencies={"third": third_dependency})
async def homepage(first: bool, second: str, third: dict) -> dict:
    return {"page": "ok"}


app = Esmerald(
    routes=[Gateway(handler=homepage, dependencies={"second": second_dependency})],
    dependencies={"first": first_dependency},
)
