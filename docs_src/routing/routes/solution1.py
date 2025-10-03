from ravyn import Ravyn, Include

app = Ravyn(
    routes=[
        Include(namespace="src.urls", name="root"),
        Include(path="/api/v1", namespace="accounts.v1.urls", name="accounts"),
    ]
)
