from ravyn import Ravyn, Include

app = Ravyn(
    routes=[
        Include(namespace="src.urls", name="root"),
        Include(namespace="accounts.v1.urls", name="accounts"),
    ]
)
