from esmerald import APIView, Esmerald, Gateway, get


class MyAPIView(APIView):
    path = "/customer/{name}"

    @get(path="/")
    def home(self, name: str) -> str:  # type: ignore[valid-type]
        return name

    @get(path="/info")
    def info(self, name: str) -> str:  # type: ignore[valid-type]
        return f"Test {name}"

    @get(path="/info/{param}")
    def info_detail(self, name: str, param: str) -> str:  # type: ignore[valid-type]
        return f"Test {name}"


app = Esmerald(routes=[Gateway(handler=MyAPIView)])
