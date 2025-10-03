from ravyn import JSON, Ravyn, Gateway, Request, get, status


@get(path="/{url}", status_code=status.HTTP_201_CREATED)
async def home(request: Request, url: str) -> JSON:
    return JSON(content=f"URL: {url}", status_code=status.HTTP_202_ACCEPTED)


app = Ravyn(routes=[Gateway(handler=home)])
