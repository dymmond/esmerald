from loguru import logger

from esmerald import get, post
from esmerald.testclient import create_client
from esmerald.utils.decorators import propagator

TOTAL_SEND = 0
TOTAL_EMAIL = 0


@get("/")
@propagator(send=["item_send", "email_send"])
async def get_item() -> dict:
    logger.info("Sending item")
    return {"item_id": 1}


@post("/receive")
@propagator(listen=["item_send"])
async def create_item() -> dict:
    global TOTAL_SEND
    TOTAL_SEND += 1
    logger.success("Received item")
    return "ok"


@propagator(listen=["email_send"])
async def listen_item_send() -> None:
    global TOTAL_EMAIL
    TOTAL_EMAIL += 1
    logger.success("Listening to email send")


@propagator(listen=["email_send"])
def listen_item_send_sync() -> None:
    global TOTAL_EMAIL
    TOTAL_EMAIL += 1
    logger.success("Listening to email send in sync mode")


def test_controller_decorator():
    with create_client(routes=[get_item, create_item]) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"item_id": 1}

        assert TOTAL_SEND == 1
        assert TOTAL_EMAIL == 2
