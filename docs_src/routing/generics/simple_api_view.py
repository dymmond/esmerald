from esmerald import SimpleAPIView, delete, get, patch, post, put


class UserAPI(SimpleAPIView):
    @get()
    def get(self) -> str:
        ...

    @post()
    def post(self) -> str:
        ...

    @put()
    def put(self) -> str:
        ...

    @patch()
    def patch(self) -> str:
        ...

    @delete()
    def delete(self) -> None:
        ...
