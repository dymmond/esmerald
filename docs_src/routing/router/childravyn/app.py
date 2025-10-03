from apps.routers.customers import router as customers_router

from ravyn import Ravyn, Include

app = Ravyn(routes=[Include("/customers", app=customers_router)])
