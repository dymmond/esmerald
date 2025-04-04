from esmerald import get, post
from esmerald.core.datastructures import ResponseHeader
from esmerald.utils.decorators import controller


@controller(path="/users")
class UserController:

    @get(path="/", response_headers={"X-Custom": ResponseHeader(value="Custom Header")})
    async def list_users(self) -> list[dict]:
        """Retrieve a list of users."""
        return [{"id": 1, "name": "John Doe"}]

    @post(path="/create")
    async def create_user(self, data: dict) -> dict:
        """Create a new user."""
        return {"message": "User created successfully", "data": data}
