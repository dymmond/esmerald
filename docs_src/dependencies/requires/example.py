from ravyn import Request, Security, HTTPException, get, Inject, Injects, Ravyn, Gateway
from lilya import status
from typing import cast, Any
from pydantic import BaseModel


class MyCustomSecurity:
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.__auto_error__ = kwargs.pop("auto_error", True)

    async def __call__(self, request: Request) -> dict[str, None]:
        api_key = request.query_params.get(self.name, None)
        if api_key:
            return cast(str, api_key)

        if self.__auto_error__:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        return None


# Instantiate the custom security scheme
api_key = MyCustomSecurity(name="key")

# Use the custom security scheme
security = Security(api_key)


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(api_key)):
    user = User(username=oauth_header)
    return user


@get(
    "/users/me",
    security=[api_key],
    dependencies={"current_user": Inject(get_current_user)},
)
def read_current_user(current_user: User = Injects()) -> Any:
    return current_user


# Start the application
app = Ravyn(
    routes=[Gateway(handler=read_current_user)],
)
