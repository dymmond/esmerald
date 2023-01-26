from esmerald import JSON, Esmerald, Gateway, Request, get, status


@get(path="/{url}", status_code=status.HTTP_201_CREATED)
async def home(request: Request, url: str) -> JSON:
    return JSON(content=f"URL: {url}", status_code=status.HTTP_202_ACCEPTED)


app = Esmerald(routes=[Gateway(handler=home)])
