from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel, field_validator
from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.msgspec import Struct
from esmerald.utils.enums import MediaType


class OpenAPIResponse(BaseModel):
    """
    The OpenAPIResponse is used for [OpenAPI](https://esmerald.dev/openapi/)
    documentation purposes and allows to describe in detail what alternative
    responses the API can return as well as the type of the return itself.

    **Example**

    ```python
    from typing import Union

    from esmerald import post
    from esmerald.openapi.datastructures import OpenAPIResponse
    from pydantic import BaseModel


    class ItemOut(BaseModel):
        sku: str
        description: str


    @post(path='/create', summary="Creates an item", responses={200: OpenAPIResponse(model=ItemOut, description="Successfully created an item")})
    async def create() -> Union[None, ItemOut]:
        ...
    ```
    """

    model: Annotated[
        Union[
            Type[BaseModel],
            List[Type[BaseModel]],
            Type[Struct],
            List[Type[Struct]],
            Type[Any],
            List[Type[Any]],
        ],
        Doc(
            """
            A `pydantic.BaseModel` type of object of a `list` of
            `pydantic.BaseModel` types of objects.

            This is parsed and displayed in the [OpenAPI](https://esmerald.dev/openapi/)
            documentation.

            **Example**

            ```python
            from esmerald.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel


            class Error(BaseModel):
                detail: str

            # Single
            OpenAPIResponse(model=Error)

            # List
            OpenAPIResponse(model=[Error])
            ```
            """
        ),
    ]
    description: Annotated[
        str,
        Doc(
            """
            Description of the response.

            This description is displayed in the [OpenAPI](https://esmerald.dev/openapi/)
            documentation.
            """
        ),
    ] = "Additional response"
    media_type: Annotated[
        MediaType,
        Doc("""The `media-type` of the response."""),
    ] = MediaType.JSON
    status_text: Annotated[
        Optional[str],
        Doc(
            """
            Description of the `status_code`. The description of the status code itself.

            This description is displayed in the [OpenAPI](https://esmerald.dev/openapi/)
            documentation.
            """
        ),
    ] = None

    @field_validator("model", mode="before")
    def validate_model(
        cls,
        model: Union[
            Type[BaseModel],
            List[Type[BaseModel]],
            Type[Struct],
            List[Type[Struct]],
            Type[Any],
            List[Type[Any]],
        ],
    ) -> Union[
        Type[BaseModel],
        List[Type[BaseModel]],
        Type[Struct],
        List[Type[Struct]],
        Type[Any],
        List[Type[Any]],
    ]:
        if isinstance(model, list) and len(model) > 1:
            raise ValueError(
                "The representation of a list of models in OpenAPI can only be a total of one. Example: OpenAPIResponse(model=[MyModel])."
            )
        return model
