from apps.routers.customers import router as customers_router

from esmerald import Esmerald, Include

app = Esmerald(routes=[Include("/customers", app=customers_router)])
