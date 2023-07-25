from datetime import datetime

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, post
from esmerald.routing.gateways import WebhookGateway
from esmerald.routing.webhooks.handlers import whpost


class Payment(BaseModel):
    is_paid: bool
    amount: float
    paid_at: datetime


@whpost("new-event")
async def new_event(data: Payment) -> None:
    ...


@post("/create")
async def create_payment(data: Payment) -> None:
    ...


app = Esmerald(
    routes=[Gateway(handler=create_payment)],
    webhooks=[WebhookGateway(handler=new_event)],
)
