from ravyn import Ravyn, Include

app = Ravyn(routes=[Include(namespace="src.urls")])
