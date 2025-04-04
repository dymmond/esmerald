from typing import Callable

import pytest

from esmerald.background import BackgroundTask, BackgroundTasks
from esmerald.responses import Response
from esmerald.routing.router import Include
from esmerald.testclient import EsmeraldTestClient, create_client


def test_async_task(test_client_factory):
    TASK_COMPLETE = False

    async def async_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(async_task)

    async def app(scope, receive, send):
        response = Response("task initiated", media_type="text/plain", background=task)
        await response(scope, receive, send)

    with create_client(routes=[Include("/", app)]) as client:
        response = client.get("/")
        assert response.text == "task initiated"
        assert TASK_COMPLETE


def test_sync_task(test_client_factory):
    TASK_COMPLETE = False

    def sync_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(sync_task)

    async def app(scope, receive, send):
        response = Response("task initiated", media_type="text/plain", background=task)
        await response(scope, receive, send)

    with create_client(routes=[Include("/", app)]) as client:
        response = client.get("/")
        assert response.text == "task initiated"
        assert TASK_COMPLETE


def test_multiple_tasks(test_client_factory: Callable[..., EsmeraldTestClient]):
    TASK_COUNTER = 0

    def increment(amount):
        nonlocal TASK_COUNTER
        TASK_COUNTER += amount

    async def app(scope, receive, send):
        tasks = BackgroundTasks()
        tasks.add_task(increment, amount=1)
        tasks.add_task(increment, amount=2)
        tasks.add_task(increment, amount=3)
        response = Response("tasks initiated", media_type="text/plain", background=tasks)
        await response(scope, receive, send)

    with create_client(routes=[Include("/", app)]) as client:
        response = client.get("/")
        assert response.text == "tasks initiated"
        assert TASK_COUNTER == 1 + 2 + 3


def test_multi_tasks_failure_avoids_next_execution(
    test_client_factory: Callable[..., EsmeraldTestClient],
) -> None:
    TASK_COUNTER = 0

    def increment():
        nonlocal TASK_COUNTER
        TASK_COUNTER += 1
        if TASK_COUNTER == 1:
            raise Exception("task failed")

    async def app(scope, receive, send):
        tasks = BackgroundTasks()
        tasks.add_task(increment)
        tasks.add_task(increment)
        response = Response("tasks initiated", media_type="text/plain", background=tasks)
        await response(scope, receive, send)

    with create_client(routes=[Include("/", app)]) as client:
        with pytest.raises(Exception):  # noqa
            client.get("/")
        assert TASK_COUNTER == 1
