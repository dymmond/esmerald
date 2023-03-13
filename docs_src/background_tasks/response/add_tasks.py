from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from esmerald import BackgroundTasks, Request, Response, post


class UserIn(BaseModel):
    email: str
    password: str


async def send_email_notification(email: str, message: str):
    """Sends an email notification"""
    send_notification(email, message)


def write_in_file(email: str):
    with open("log.txt", mode="w") as log:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"Notification sent @ {now} to: {email}"
        log.write(content)


@post("/register")
async def create_user(data: UserIn, request: Request) -> Response(Dict[str, str]):
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        send_email_notification, email=request.user.email, message="Thank you for registering."
    )
    background_tasks.add_task(write_in_file, email=request.user.email)

    return Response({"message": "Email sent"}, background=background_tasks)
