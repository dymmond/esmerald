from datetime import datetime

from pydantic import BaseModel

from ravyn import Ravyn, Gateway, post
from ravyn.routing.gateways import WebhookGateway
from ravyn.routing.webhooks import whpost


class Payment(BaseModel):
    is_paid: bool
    amount: float
    paid_at: datetime


@whpost("new-event")
async def new_event(data: Payment) -> None: ...


@post("/create")
async def create_payment(data: Payment) -> None: ...


app = Ravyn(
    routes=[Gateway(handler=create_payment)],
    webhooks=[WebhookGateway(handler=new_event)],
)
