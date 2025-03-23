import anyio
import pytest
from loguru import logger

from esmerald import get, post
from esmerald.testclient import create_client
from esmerald.utils.decorators import propagator

TOTAL_SEND = 0
TOTAL_EMAIL = 0

send_lock = anyio.Lock()
email_lock = anyio.Lock()

send_event = anyio.Event()
email_event = anyio.Event()


@get("/")
@propagator(send=["item_send", "email_send"])
async def get_item() -> dict:
    """Simulates sending an item, triggering events."""
    logger.info("Sending item")
    return {"item_id": 1}


@post("/receive")
@propagator(listen=["item_send"])
async def create_item() -> dict:
    """Handles received items and updates the counter safely."""
    global TOTAL_SEND
    async with send_lock:
        TOTAL_SEND += 1
    logger.success("Received item")
    send_event.set()  # ✅ FIX: No await here
    return "ok"


@propagator(listen=["email_send"])
async def listen_item_send() -> None:
    """Async listener for 'email_send' events."""
    global TOTAL_EMAIL
    async with email_lock:
        TOTAL_EMAIL += 1
    logger.success("Listening to email send")
    email_event.set()  # ✅ FIX: No await here


@propagator(listen=["email_send"])
def listen_item_send_sync() -> None:
    """Sync listener for 'email_send' events."""
    global TOTAL_EMAIL
    TOTAL_EMAIL += 1
    logger.success("Listening to email send in sync mode")
    email_event.set()  # ✅ FIX: No await here


@pytest.mark.asyncio
async def test_propagator():
    """Runs the test within a proper AnyIO-managed event loop."""
    with create_client(routes=[get_item, create_item]) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"item_id": 1}

        # ✅ Allow time for async events to process
        await send_event.wait()
        await email_event.wait()

        # ✅ Now check values
        assert TOTAL_SEND == 1
        assert TOTAL_EMAIL == 2
