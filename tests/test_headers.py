# from esmerald import Gateway, Header, ORJSONResponse, post
# from esmerald.testclient import create_client
# from pydantic import BaseModel, EmailStr


# class User(BaseModel):
#     name: str
#     email: EmailStr


# @post(path="/create")
# async def create_user(
#     data: User,
#     token: str = Header(value="X-API-TOKEN"),
# ) -> ORJSONResponse:
#     return ORJSONResponse({"token": token, "user": data})


# def xtest_headers_field(test_client_factory):
#     user = {"name": "Esmerald", "email": "test@esmerald.com"}
#     with create_client(routes=[Gateway(handler=create_user)]) as client:
#         import ipdb

#         ipdb.sset_trace()
#         response = client.post("/create", data=user, headers={"X-API-TOKEN": "my-token"})
