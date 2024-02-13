from esmerald import SimpleAPIView, delete, get, patch, post, put


class UserAPI(SimpleAPIView):
    @get()
    async def get(self) -> str: ...

    @post()
    async def post(self) -> str: ...

    @put()
    async def put(self) -> str: ...

    @patch()
    async def patch(self) -> str: ...

    @delete()
    async def delete(self) -> None: ...
