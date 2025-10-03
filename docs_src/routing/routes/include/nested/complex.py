from ravyn import Ravyn, Gateway, Include, get


@get()
async def me() -> None: ...


app = Ravyn(
    routes=[
        Include(
            "/",
            routes=[
                Include(
                    "/another",
                    routes=[
                        Include(
                            "/multi",
                            routes=[
                                Include(
                                    "/nested",
                                    routes=[
                                        Include(
                                            "/routing",
                                            routes=[
                                                Gateway(path="/me", handler=me),
                                                Include(
                                                    path="/imported",
                                                    namespace="myapp.routes",
                                                ),
                                            ],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    ]
)
