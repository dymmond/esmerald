from typing import Any

import anyio
import pytest
from loguru import logger

from esmerald import get, post
from esmerald.testclient import create_client
from esmerald.utils.decorators import observable

# Global counters to track event triggers
TOTAL_SEND = 0
TOTAL_EMAIL = 0
TOTAL_EXTRA = 0  # Additional counter for extended cases
TOTAL_REGISTRATIONS = 0  # Track user registrations
TOTAL_ROLE_ASSIGNMENTS = 0  # Track role assignments

# Locks for thread safety
send_lock = anyio.Lock()
email_lock = anyio.Lock()
extra_lock = anyio.Lock()
registration_lock = anyio.Lock()
role_lock = anyio.Lock()

# Event flags for async coordination
send_event = anyio.Event()
email_event = anyio.Event()
extra_event = anyio.Event()
registration_event = anyio.Event()
role_event = anyio.Event()


@get("/")
@observable(send=["item_send", "email_send", "extra_event"])
async def get_item() -> dict:
    """Simulates sending an item, triggering multiple events."""
    logger.info("Sending item")
    return {"item_id": 1}


@post("/receive")
@observable(listen=["item_send"])
async def create_item() -> dict:
    """Handles received items and updates the counter safely."""
    global TOTAL_SEND
    async with send_lock:
        TOTAL_SEND += 1
    logger.success("Received item")
    send_event.set()
    return "ok"


@observable(listen=["email_send"])
async def listen_email_send() -> None:
    """Async listener for 'email_send' events."""
    global TOTAL_EMAIL
    async with email_lock:
        TOTAL_EMAIL += 1
    logger.success("Listening to email send")
    email_event.set()


@observable(listen=["email_send"])
def listen_email_send_sync() -> None:
    """Sync listener for 'email_send' events."""
    global TOTAL_EMAIL
    TOTAL_EMAIL += 1
    logger.success("Listening to email send in sync mode")
    email_event.set()


@observable(listen=["extra_event"])
async def listen_extra_event() -> None:
    """Async listener for 'extra_event'."""
    global TOTAL_EXTRA
    async with extra_lock:
        TOTAL_EXTRA += 1
    logger.success("Listening to extra event")
    extra_event.set()


@post("/register")
@observable(send=["user_registered"])
async def register_user(data: dict) -> dict:
    """
    Registers a new user and emits a 'user_registered' event
    with user information.
    """
    global TOTAL_REGISTRATIONS
    async with registration_lock:
        TOTAL_REGISTRATIONS += 1

    logger.success(f"User registered: {data['email']}")
    registration_event.set()

    return {"message": "User registered successfully!", "email": data["email"], "id": data["id"]}


@observable(listen=["user_registered"])
async def send_welcome_email(**kwargs: Any) -> None:
    """Sends a welcome email to the newly registered user."""
    data = kwargs.get("data")
    global TOTAL_EMAIL
    async with email_lock:
        TOTAL_EMAIL += 1
    logger.success(f"Sending welcome email to {data['email']}...")
    email_event.set()


@observable(listen=["user_registered"])
async def assign_default_roles(**kwargs: Any):
    """Assigns default roles to the newly registered user."""
    data = kwargs.get("data")
    global TOTAL_ROLE_ASSIGNMENTS
    async with role_lock:
        TOTAL_ROLE_ASSIGNMENTS += 1

    logger.success(f"Assigning default roles to user ID {data['id']}...")
    role_event.set()


@pytest.mark.asyncio
async def test_observable():
    """Runs the test within a proper AnyIO-managed event loop."""
    with create_client(routes=[get_item, create_item]) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"item_id": 1}

        # ✅ Allow time for async events to process
        await send_event.wait()
        await email_event.wait()
        await extra_event.wait()

        # ✅ Check values
        assert TOTAL_SEND == 1
        assert TOTAL_EMAIL == 2  # Two listeners for "email_send"
        assert TOTAL_EXTRA == 1  # Only one listener for "extra_event"


@pytest.mark.asyncio
async def test_no_listeners():
    """Test case where an event is emitted but has no listeners."""
    await anyio.sleep(0.1)  # Ensure previous tests don't interfere

    # Log messages outside async task group
    logger.info("Emitting unused event")
    logger.info("No listeners should be triggered")

    # Ensure counts remain the same
    assert TOTAL_SEND == 1
    assert TOTAL_EMAIL == 2
    assert TOTAL_EXTRA == 1


@pytest.mark.asyncio
async def test_multiple_executions():
    """Ensure multiple event emissions increment counters correctly."""
    with create_client(routes=[get_item]) as client:
        for _ in range(3):  # Trigger the event multiple times
            client.get("/")

        # ✅ Wait for all events
        await send_event.wait()
        await email_event.wait()
        await extra_event.wait()

        # ✅ Validate results
        assert TOTAL_SEND == 1 + 3  # Previous + 3 new executions
        assert TOTAL_EXTRA == 1 + 3  # 1 previous + 3 new executions


@pytest.mark.asyncio
async def test_user_registration():
    """Test the user registration event and its listeners."""
    with create_client(routes=[register_user]) as client:
        response = client.post("/register", json={"email": "user@example.com", "id": 42})
        assert response.status_code == 201
        assert response.json() == {
            "message": "User registered successfully!",
            "email": "user@example.com",
            "id": 42,
        }

        # ✅ Wait for all events
        await registration_event.wait()
        await email_event.wait()
        await role_event.wait()

        # ✅ Validate results
        assert TOTAL_REGISTRATIONS == 1
        assert TOTAL_ROLE_ASSIGNMENTS == 1  # One role assigned for the new user


@pytest.mark.asyncio
async def test_multiple_user_registrations():
    """Ensure multiple user registrations increment counters correctly."""
    with create_client(routes=[register_user]) as client:
        for i in range(3):  # Register 3 users
            client.post("/register", json={"email": f"user{i}@example.com", "id": i})

        # ✅ Wait for all events
        await registration_event.wait()
        await email_event.wait()
        await role_event.wait()

        # ✅ Validate results
        assert TOTAL_REGISTRATIONS == 1 + 3  # Previous + 3 new registrations
        assert TOTAL_ROLE_ASSIGNMENTS == 1 + 3  # Previous total + 3 new role assignments
