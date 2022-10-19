from esmerald import Esmerald, Include

app = Esmerald(routes=[Include("src.urls")])
