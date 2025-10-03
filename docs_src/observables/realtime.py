from ravyn import post
from ravyn.utils.decorators import observable


@post("/comment")
@observable(send=["new_comment"])
async def add_comment():
    return {"message": "Comment added!"}


@observable(listen=["new_comment"])
async def send_notification():
    print("Sending notification about the new comment...")
