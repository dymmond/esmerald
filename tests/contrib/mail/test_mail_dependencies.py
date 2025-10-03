from typing import Any

import pytest
from lilya.contrib.mail import EmailMessage
from lilya.contrib.mail.backends.inmemory import InMemoryBackend
from lilya.contrib.mail.mailer import Mailer
from lilya.contrib.mail.startup import setup_mail

from ravyn import Gateway, Inject, Injects, Ravyn, get, post
from ravyn.contrib.mail.dependencies import Mail
from ravyn.testclient import RavynTestClient

pytestmark = pytest.mark.asyncio


async def test_mail_dependency_injection(tmp_path, test_client_factory):
    backend = InMemoryBackend()

    # Attach mailer to app

    @post("/send", dependencies={"mailer": Mail})
    async def send_email(mailer: Any = Injects()) -> dict[str, bool]:
        msg = EmailMessage(subject="Hello", to=["a@test"], body_text="hi")
        await mailer.send(msg)
        return {"ok": True}

    app = Ravyn(
        routes=[Gateway(handler=send_email)],
    )

    setup_mail(app, backend=backend, template_dir=str(tmp_path))

    client = RavynTestClient(app)

    # Call endpoint
    response = client.post("/send")

    assert response.status_code == 201
    assert response.json() == {"ok": True}

    # Ensure message was delivered through backend
    assert len(backend.outbox) == 1
    assert backend.outbox[0].subject == "Hello"
    assert backend.outbox[0].body_text == "hi"
    assert backend.outbox[0].to == ["a@test"]


async def test_mail_dependency_reuses_same_instance(tmp_path):
    backend = InMemoryBackend()

    calls: list[Mailer] = []

    @get("/ping", dependencies={"mailer": Mail})
    async def ping(mailer: Any = Injects()) -> dict[str, bool]:
        calls.append(mailer)
        return {"ok": True}

    app = Ravyn(
        routes=[Gateway(handler=ping)],
    )

    setup_mail(app, backend=backend, template_dir=str(tmp_path))

    client = RavynTestClient(app)

    # Call twice
    client.get("/ping")
    client.get("/ping")

    assert len(calls) == 2

    # Both injections should resolve to the same Mailer instance
    assert calls[0] is calls[1]
    assert isinstance(calls[0], Mailer)


async def test_mail_dependency_override(tmp_path):
    backend = InMemoryBackend()

    class FakeMailer:
        def __init__(self):
            self.sent = []

        async def send(self, message: EmailMessage):
            self.sent.append(message)

    fake_mailer = FakeMailer()

    async def _resolve_fake(request: Any, **kwargs: Any) -> FakeMailer:
        return fake_mailer

    FakeMail = Inject(_resolve_fake)

    @post("/send", dependencies={"mailer": FakeMail})
    async def send_email(mailer: Any = Injects()) -> dict[str, bool]:
        msg = EmailMessage(subject="fake", to=["x@test"], body_text="hi")
        await mailer.send(msg)
        return {"ok": True}

    app = Ravyn(
        routes=[Gateway(handler=send_email)],
    )

    setup_mail(app, backend=backend, template_dir=str(tmp_path))

    client = RavynTestClient(app)
    response = client.post("/send")

    assert response.status_code == 201
    assert response.json() == {"ok": True}

    assert len(fake_mailer.sent) == 1
    assert fake_mailer.sent[0].subject == "fake"


async def test_mail_dependency_misconfigured_state(tmp_path):
    @get("/bad", dependencies={"mailer": Mail})
    async def bad(mailer: Any = Injects()) -> dict[str, bool]:
        return {"ok": True}

    app = Ravyn(
        routes=[Gateway(handler=bad)],
    )
    # Deliberately attach wrong object
    app.state.mailer = object()

    client = RavynTestClient(app)

    response = client.get("/bad")

    assert response.status_code == 500
