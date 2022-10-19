from esmerald import Esmerald, Gateway, Include, UJSONResponse, delete


@delete(path="/{item_id:int}")
def delete_item(item_id: int) -> int:
    # logic that deletes an item
    ...


@delete(path="/")
def another_delete(item_id: int) -> UJSONResponse:
    # logic that deletes an item
    ...


app = Esmerald(
    routes=[
        Include(
            "/delete",
            routes=[
                Gateway(handler=delete_item),
                Gateway(path="/last/{item_id:int}", handler=another_delete),
            ],
        ),
    ]
)
