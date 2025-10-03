from ravyn import JSON, Ravyn, Gateway, Request, get, status


@get(path="/{url}", status_code=status.HTTP_202_ACCEPTED)
async def home(request: Request, url: str) -> JSON:
    return JSON(content=f"URL: {url}")


app = Ravyn(routes=[Gateway(handler=home)])
