from esmerald import Esmerald, Gateway, Include, Inject, get


def first_dependency() -> int:
    return 20


def second_dependency(number: int) -> bool:
    return number >= 5


@get("/validate")
async def me(is_valid: bool) -> bool:
    return is_valid


app = Esmerald(
    routes=[
        Include(
            routes=[Gateway(handler=me)],
            dependencies={
                "is_valid": second_dependency,
            },
        )
    ],
    dependencies={"number": first_dependency},
)
