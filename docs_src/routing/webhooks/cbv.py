from datetime import datetime

from pydantic import BaseModel

from esmerald import APIView, Esmerald, Gateway, post
from esmerald.routing.gateways import WebhookGateway
from esmerald.routing.webhooks.handlers import whpost


class Payment(BaseModel):
    is_paid: bool
    amount: float
    paid_at: datetime


class PaymentWebhook(APIView):
    @whpost("new-event")
    async def new_event(self, data: Payment) -> None: ...

    @whpost("payments")
    async def new_payment(self, data: Payment) -> None: ...


@post("/create")
async def create_payment(data: Payment) -> None: ...


app = Esmerald(
    routes=[Gateway(handler=create_payment)],
    webhooks=[WebhookGateway(handler=PaymentWebhook)],
)
