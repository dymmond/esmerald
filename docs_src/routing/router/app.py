from apps.routers.customers import router as customers_router

from esmerald import Esmerald

app = Esmerald()
app.add_router(customers_router)
