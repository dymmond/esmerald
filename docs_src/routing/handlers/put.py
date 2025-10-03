from ravyn import Ravyn, Gateway, JSONResponse, put


@put(path="/update/{item_id:int}")
def update(item_id: int) -> int:
    return item_id


@put(path="/")
def another_update(item_id: int) -> JSONResponse:
    return JSONResponse({"Success", {item_id}})


app = Ravyn(
    routes=[
        Gateway(handler=update),
        Gateway(path="/last/{item_id:int}", handler=another_update),
    ]
)
