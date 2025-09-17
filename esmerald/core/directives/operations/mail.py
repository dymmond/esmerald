from __future__ import annotations

import asyncio
from typing import Annotated

from lilya.contrib.mail import EmailMessage
from lilya.contrib.mail.backends.console import ConsoleBackend
from lilya.contrib.mail.mailer import Mailer
from sayer import Option, Sayer, command, error, success


@command
def sendtest(
    to: Annotated[
        str,
        Option(help="Recipient email address. Can be used multiple times.", required=True),
    ],
    subject: Annotated[
        str, Option(default="Test email", help="Subject of the email.", show_default=True)
    ],
    text: Annotated[str | None, Option(help="Plain text body.", required=False)] = None,
    html: Annotated[str | None, Option(help="HTML body.", required=False)] = None,
    backend: Annotated[
        str,
        Option(default="console", help="Backend to use for sending (default: console)."),
    ] = "console",
) -> None:
    """Send a test email using Lilya's mail contrib system.

    Examples:

      esmerald mail sendtest --to user@example.com --subject 'Hello' --text 'Plain message'

      esmerald mail sendtest --to user@example.com --subject 'Hello' --html '<p>Hello world</p>'
    """

    async def _send() -> None:
        if backend == "console":
            b = ConsoleBackend()
        else:
            error(f"Unsupported backend: {backend}")
            return

        mailer = Mailer(backend=b)
        msg = EmailMessage(
            subject=subject,
            to=[to],
            body_text=text,
            body_html=html,
            from_email="noreply@lilya.local",
        )
        await mailer.send(msg)
        success(f"Test email sent to {to} using {backend} backend.")

    asyncio.run(_send())


mail = Sayer(help="Send a test email using Lilya's mail contrib system.")

mail.add_command(sendtest)
