from pydantic import BaseModel

from ravyn import BackgroundTask, JSONResponse, post


class UserIn(BaseModel):
    email: str
    password: str


async def send_email_notification(message: str):
    """Sends an email notification"""
    send_notification(message)


@post(
    "/register",
    background=BackgroundTask(send_email_notification, message="Account created"),
)
async def create_user(data: UserIn) -> JSONResponse:
    JSONResponse({"message": "Created"})
