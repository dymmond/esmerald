from datetime import datetime

from pydantic import BaseModel

from ravyn import Controller, Ravyn, Gateway, post
from ravyn.routing.gateways import WebhookGateway
from ravyn.routing.webhooks import whpost


class Payment(BaseModel):
    is_paid: bool
    amount: float
    paid_at: datetime


class PaymentWebhook(Controller):
    @whpost("new-event")
    async def new_event(self, data: Payment) -> None: ...

    @whpost("payments")
    async def new_payment(self, data: Payment) -> None: ...


@post("/create")
async def create_payment(data: Payment) -> None: ...


app = Ravyn(
    routes=[Gateway(handler=create_payment)],
    webhooks=[WebhookGateway(handler=PaymentWebhook)],
)
