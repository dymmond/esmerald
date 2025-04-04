from typing import Any, Callable, Iterable, Type, cast

import msgspec
from msgspec import ValidationError
from pydantic._internal._schema_generation_shared import (
    GetJsonSchemaHandler as GetJsonSchemaHandler,
)
from pydantic_core.core_schema import (
    CoreSchema,
    PlainValidatorFunctionSchema,
    with_info_plain_validator_function,
)

REF_TEMPLATE = "#/components/schemas/{name}"


class Struct(msgspec.Struct):
    """
    `Struct` object is the `esmerald.datastructures.msgspec` integration
    with Pydantic.

    When you want to integrate msgspec with your existing Pydantic models,
    you can simply use this datastructure directly to integrate in cleaner
    way. This will provide all the necessary data for Pydantic to generate
    the necessary schema data.

    This datastructure subclasses the `msgspec.Struct` directly which means
    there is no additional unique information added besides the
    Pydantic unique functionalities.

    **Example**

    ```python
    from pydantic import BaseModel

    from esmerald.datastructures.msgspec import Struct

    class User(Struct):
        name: str
        email: Union[str, None] = None


    class BaseUser(BaseModel):
        model_config = {"arbitrary_types_allowed": True}
        user: User

    ```
    """

    @classmethod
    def __get_validators__(cls: Type["Struct"]) -> Iterable[Callable[..., Any]]:
        yield cls.validate

    @classmethod
    def validate(cls: Type["Struct"], v: Any) -> Any:
        if not isinstance(v, msgspec.Struct):
            raise ValueError(f"Expected `esmerald.datastructures.msgspec.Struct`, got: {type(v)}")
        return v

    @classmethod
    def _validate(cls, __input_value: Any, _: Any) -> "Struct":
        try:
            return msgspec.json.decode(msgspec.json.encode(__input_value), type=cls)
        except ValidationError as e:
            raise e

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Any:
        _, schema_definitions = msgspec.json.schema_components(
            types=(cls,), ref_template=REF_TEMPLATE
        )
        return schema_definitions[cls.__name__]

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: Callable[[Any], CoreSchema]
    ) -> CoreSchema:
        return cast(
            PlainValidatorFunctionSchema,
            with_info_plain_validator_function(cls._validate),
        )
