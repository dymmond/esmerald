from ravyn import post
from ravyn.utils.decorators import observable


@post("/login")
@observable(send=["user_logged_in"])
async def login():
    return {"message": "User logged in!"}


@observable(listen=["user_logged_in"])
async def log_login_activity():
    print("Logging user login activity...")
