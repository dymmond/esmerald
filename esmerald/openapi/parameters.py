from typing import TYPE_CHECKING, Any, Dict, List, cast

from esmerald.enums import ParamType
from esmerald.exceptions import ImproperlyConfigured
from esmerald.openapi.schema import create_schema
from esmerald.utils.constants import REQUIRED, RESERVED_KWARGS
from esmerald.utils.dependency import is_dependency_field
from openapi_schemas_pydantic.v3_1_0.parameter import Parameter
from pydantic.fields import Undefined


if TYPE_CHECKING:
    from esmerald.routing.router import HTTPHandler
    from esmerald.types import Dependencies
    from openapi_schemas_pydantic.v3_1_0.schema import Schema
    from pydantic import BaseModel
    from pydantic.fields import ModelField


def create_path_parameter_schema(
    path_parameter: Any, field: "ModelField", create_examples: bool
) -> "Schema":
    field.sub_fields = None
    field.outer_type_ = path_parameter["type"]
    return create_schema(field=field, create_examples=create_examples)


class ParameterCollection:
    def __init__(self, handler: "HTTPHandler") -> None:
        self.handler = handler
        self._parameters: Dict[str, Parameter] = {}

    def add(self, parameter: Parameter) -> None:
        if parameter.name not in self._parameters:
            self._parameters[parameter.name] = parameter
            return
        pre_existing = self._parameters[parameter.name]
        if parameter == pre_existing:
            return
        raise ImproperlyConfigured(
            f"OpenAPI schema generation for handler `{self.handler}` detected multiple parameters named "
            f"'{parameter.name}' with different types."
        )

    def list(self) -> List[Parameter]:
        return list(self._parameters.values())


def create_parameter(
    model_field: "ModelField",
    parameter_name: str,
    path_paramaters: Any,
    create_examples: bool,
) -> Parameter:
    schema = None
    is_required = (
        cast("bool", model_field.required) if model_field.required is not Undefined else False
    )
    extra = model_field.field_info.extra
    if any(path_param["name"] == parameter_name for path_param in path_paramaters):
        param_in = ParamType.PATH
        is_required = True
        path_parameter = [p for p in path_paramaters if parameter_name in p["name"]][0]
        schema = create_path_parameter_schema(
            path_parameter=path_parameter,
            field=model_field,
            create_examples=create_examples,
        )
    elif extra.get(ParamType.HEADER):
        parameter_name = extra[ParamType.HEADER]
        param_in = ParamType.HEADER
        is_required = model_field.field_info.extra[REQUIRED]
    elif extra.get(ParamType.COOKIE):
        parameter_name = extra[ParamType.COOKIE]
        param_in = ParamType.COOKIE
        is_required = model_field.field_info.extra[REQUIRED]
    else:
        param_in = ParamType.QUERY
        parameter_name = extra.get(ParamType.QUERY) or parameter_name

    if not schema:
        schema = create_schema(field=model_field, create_examples=create_examples)

    return Parameter(
        name=parameter_name,
        param_in=param_in,
        required=is_required,
        param_schema=schema,
        description=schema.description,
    )


def get_recursive_handler_parameters(
    field_name: str,
    model_field: "ModelField",
    dependencies: "Dependencies",
    handler: "HTTPHandler",
    path_parameters: Any,
    create_examples: bool,
):
    if field_name not in dependencies:
        return [
            create_parameter(
                model_field=model_field,
                parameter_name=field_name,
                path_paramaters=path_parameters,
                create_examples=create_examples,
            )
        ]
    dependency_fields = cast("BaseModel", dependencies[field_name].signature_model).__fields__

    return create_parameter_for_handler(
        handler, dependency_fields, path_parameters, create_examples
    )


def create_parameter_for_handler(
    handler: "HTTPHandler",
    handler_fields: Dict[str, "ModelField"],
    path_parameters: Any,
    create_examples: bool,
):

    parameters = ParameterCollection(handler=handler)
    dependencies = handler.get_dependencies()

    for field_name, model_field in filter(
        lambda items: items[0] not in RESERVED_KWARGS and items[0] not in {},
        handler_fields.items(),
    ):
        if is_dependency_field(model_field.field_info) and field_name not in dependencies:
            continue

        for parameter in get_recursive_handler_parameters(
            field_name=field_name,
            model_field=model_field,
            dependencies=dependencies,
            handler=handler,
            path_parameters=path_parameters,
            create_examples=create_examples,
        ):
            parameters.add(parameter)

    return parameters.list()
