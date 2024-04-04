from esmerald import Esmerald, Include

app = Esmerald(routes=[Include(namespace="src.urls")])
