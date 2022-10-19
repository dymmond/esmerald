from esmerald import Esmerald, Gateway, UJSONResponse, put


@put(path="/update/{item_id:int}")
def update(item_id: int) -> int:
    return item_id


@put(path="/")
def another_update(item_id: int) -> UJSONResponse:
    return UJSONResponse({"Success", {item_id}})


app = Esmerald(
    routes=[
        Gateway(handler=update),
        Gateway(path="/last/{item_id:int}", handler=another_update),
    ]
)
