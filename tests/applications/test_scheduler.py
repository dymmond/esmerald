from esmerald.schedulers import AsyncIOScheduler
from esmerald.testclient import create_client


def test_default_scheduler(test_client_factory):
    with create_client([], enable_scheduler=True) as client:
        app = client.app

        assert app.scheduler_class == AsyncIOScheduler
