from typing import Dict

from pydantic import BaseModel

from esmerald import BackgroundTask, Request, Response, post


class UserIn(BaseModel):
    email: str
    password: str


async def send_email_notification(email: str, message: str):
    """Sends an email notification"""
    send_notification(email, message)


@post("/register")
async def create_user(data: UserIn, request: Request) -> Response(Dict[str, str]):
    return Response(
        {"message": "Email sent"},
        background=BackgroundTask(
            send_email_notification,
            email=request.user.email,
            message="Thank you for registering.",
        ),
    )
