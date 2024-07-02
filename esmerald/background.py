from typing import Any, Callable, List, Optional

from lilya.background import Task, Tasks
from typing_extensions import ParamSpec

P = ParamSpec("P")


class BackgroundTask(Task):
    """
    `BackgroundTask` as a single instance can be easily achieved.

    **Example**

    ```python
    from pydantic import BaseModel

    from esmerald import BackgroundTask, JSONResponse, post


    class UserIn(BaseModel):
        email: str
        password: str


    async def send_email_notification(message: str):
        '''
        Sends an email notification
        '''
        send_notification(message)


    @post(
        "/register",
        background=BackgroundTask(send_email_notification, message="Account created"),
    )
    async def create_user(data: UserIn) -> JSONResponse:
        JSONResponse({"message": "Created"})
    ```
    """

    def __init__(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__(func, *args, **kwargs)


class BackgroundTasks(Tasks):
    """
    Alternatively, the `BackgroundTasks` can also be used to be passed
    in.

    **Example**

    ```python
    from datetime import datetime

    from pydantic import BaseModel

    from esmerald import BackgroundTask, BackgroundTasks, JSONResponse, post


    class UserIn(BaseModel):
        email: str
        password: str


    async def send_email_notification(message: str):
        '''
        Sends an email notification
        '''
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
    ```
    """

    def __init__(self, tasks: Optional[List[BackgroundTask]] = None):
        super().__init__(tasks=tasks)
