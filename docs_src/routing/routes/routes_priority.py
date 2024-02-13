from esmerald import Esmerald, Gateway, get


@get()
async def user() -> dict: ...


@get()
async def active_user() -> dict: ...


# Don't do this: `/users/me`` will never match the incoming requests.
app = Esmerald(
    routes=[
        Gateway("/users/{username}", handler=user),
        Gateway("/users/me", handler=active_user),
    ]
)

# Do this: `/users/me` is tested first and both cases will work.
app = Esmerald(
    routes=[
        Gateway("/users/me", handler=active_user),
        Gateway("/users/{username}", handler=user),
    ]
)
