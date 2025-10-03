from ravyn import Ravyn, Include

app = Ravyn(
    routes=[
        Include(
            "/",
            routes=[
                Include(path="/one", namespace="src.urls"),
                Include(path="/two", namespace="accounts.v1.urls", name="accounts"),
            ],
            name="root",
        ),
    ]
)
