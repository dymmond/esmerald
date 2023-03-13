from datetime import datetime

from pydantic import BaseModel

from esmerald import BackgroundTask, BackgroundTasks, JSONResponse, post


class UserIn(BaseModel):
    email: str
    password: str


async def send_email_notification(message: str):
    """Sends an email notification"""
    send_notification(message)


def write_in_file():
    with open("log.txt", mode="w") as log:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"Notification sent @ {now}"
        log.write(content)


@post(
    "/register",
    background=BackgroundTasks(
        tasks=[
            BackgroundTask(send_email_notification, message="Account created"),
            BackgroundTask(write_in_file),
        ]
    ),
)
async def create_user(data: UserIn) -> JSONResponse:
    JSONResponse({"message": "Created"})
