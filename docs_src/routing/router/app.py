from apps.routers.customers import router as customers_router

from ravyn import Ravyn

app = Ravyn()
app.add_router(customers_router)
