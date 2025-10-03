from ravyn import Ravyn, Gateway, Include, Inject, get


def first_dependency() -> int:
    return 20


def second_dependency(number: int) -> bool:
    return number >= 5


@get("/validate")
async def me(is_valid: bool) -> bool:
    return is_valid


app = Ravyn(
    routes=[
        Include(
            routes=[Gateway(handler=me)],
            dependencies={
                "is_valid": Inject(second_dependency),
            },
        )
    ],
    dependencies={"number": Inject(first_dependency)},
)
