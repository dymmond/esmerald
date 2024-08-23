import inspect
from functools import cached_property, lru_cache
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union, _GenericAlias, cast, get_args

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from esmerald.encoders import ENCODER_TYPES
from esmerald.enums import EncodingType
from esmerald.openapi.params import ResponseParam
from esmerald.params import Body
from esmerald.utils.constants import DATA, PAYLOAD
from esmerald.utils.models import create_field_model

if TYPE_CHECKING:
    from esmerald.routing.router import HTTPHandler, WebhookHandler


@lru_cache
def convert_annotation_to_pydantic_model(field_annotation: Any) -> Any:
    """
    Converts any annotation of the body into a Pydantic
    base model.

    This is used for OpenAPI representation purposes only.

    Esmerald will try internally to convert the model into a Pydantic BaseModel,
    this will serve as representation of the model in the documentation but internally,
    it will use the native type to validate the data being sent and parsed in the
    payload/data field.
    """
    annotation_args = get_args(field_annotation)
    if isinstance(field_annotation, _GenericAlias):
        annotations = tuple(convert_annotation_to_pydantic_model(arg) for arg in annotation_args)
        field_annotation.__args__ = annotations
        return field_annotation

    if (
        not isinstance(field_annotation, BaseModel)
        and any(encoder.is_type(field_annotation) for encoder in ENCODER_TYPES)
        and inspect.isclass(field_annotation)
    ):
        field_definitions: Dict[str, Any] = {}

        for name, annotation in field_annotation.__annotations__.items():
            field_definitions[name] = (annotation, ...)
        return create_model(field_annotation.__name__, **field_definitions)
    return field_annotation


def get_field_definition(param: "FieldInfo") -> Tuple[Any, Any]:
    """
    This method will make sure that __future__ references are resolved by
    the Any type. This is necessary because the signature model will be
    generated before the actual type is resolved.
    """

    annotation = Any if isinstance(param.annotation, str) else param.annotation

    if param.default:
        definition = annotation, param.default
    elif not param.is_required():
        definition = annotation, ...
    else:
        definition = annotation, None
    return definition


def get_original_data_field(
    handler: Union["HTTPHandler", "WebhookHandler", Any]
) -> Any:  # pragma: no cover
    """
    The field used for the payload body.

    This builds a model for the required data field. Validates the type of encoding
    being passed and builds a model if a datastructure is evaluated.
    """
    if (
        DATA in handler.signature_model.model_fields
        or PAYLOAD in handler.signature_model.model_fields
    ):
        data_or_payload = DATA if DATA in handler.signature_model.model_fields else PAYLOAD
        data = handler.signature_model.model_fields[data_or_payload]

        if not isinstance(data, Body):
            body = Body(alias="body")
            for key, _ in data._attributes_set.items():
                setattr(body, key, getattr(data, key, None))
        else:
            body = data

        # Check the annotation type
        body.annotation = convert_annotation_to_pydantic_model(body.annotation)  # type: ignore

        if not body.title:
            body.title = f"Body_{handler.operation_id}"

        # For everything else that is not MULTI_PART
        extra = cast("Dict[str, Any]", body.json_schema_extra) or {}
        if extra.get("media_type", EncodingType.JSON) != EncodingType.MULTI_PART:
            return body

        # For Uploads and Multi Part
        args = get_args(body.annotation)
        name = "File" if not args else "Files"

        model = create_field_model(field=body, name=name, model_name=body.title)
        data_field = Body(annotation=model, title=body.title)

        for key, _ in data._attributes_set.items():
            if key != "annotation":
                setattr(data_field, key, getattr(body, key, None))

        return data_field


def get_data_field(
    handler: Union["HTTPHandler", "WebhookHandler", Any]
) -> Any:  # pragma: no cover
    """
    The field used for the payload body.

    This builds a model for the required data field. Validates the type of encoding
    being passed and builds a model if a datastructure is evaluated.
    """
    # return get_original_data_field(handler)

    is_data_or_payload = (
        DATA
        if DATA in handler.signature_model.model_fields
        else (PAYLOAD if PAYLOAD in handler.signature_model.model_fields else None)
    )
    body_fields_set = set()
    body_fields: Dict[str, FieldInfo] = {}

    if is_data_or_payload is not None:
        body_fields_set.add(is_data_or_payload)
        body_fields[is_data_or_payload] = handler.signature_model.model_fields[is_data_or_payload]

    for name, field in handler.signature_model.model_fields.items():
        if name in body_fields_set:
            continue

        body_fields_set.add(name)
        body_fields[name] = field

    # Set the field definitions
    field_definitions = {name: get_field_definition(param) for name, param in body_fields.items()}

    # Create the model from the field definitions
    model = create_model(
        "DataField", __config__={"arbitrary_types_allowed": True}, **field_definitions
    )

    # Create the body field
    body = Body(annotation=model, title=f"Body_{handler.operation_id}")

    # Check the annotation type
    body.annotation = convert_annotation_to_pydantic_model(body.annotation)  # type: ignore

    if not body.title:
        body.title = f"Body_{handler.operation_id}"

    return body


class OpenAPIFieldInfoMixin:
    """
    Used for validating model fields necessary for the
    OpenAPI parsing only.

    Don't use this anywhere else.
    """

    @cached_property
    def response_models(self) -> Dict[int, Any]:
        """
        The models converted into pydantic fields with the model used for OpenAPI.

        The response models can be a list representation or a single object representation.
        If another type of object is passed through the `model`, an Assertation error is raised.
        """
        responses: Dict[int, ResponseParam] = {}
        if self.responses:
            for status_code, response in self.responses.items():
                model = response.model[0] if isinstance(response.model, list) else response.model

                annotation = (
                    List[model] if isinstance(response.model, list) else model  # type: ignore
                )

                responses[status_code] = ResponseParam(
                    annotation=convert_annotation_to_pydantic_model(annotation),
                    description=response.description,
                    alias=model.__name__,
                )
        return responses

    @cached_property
    def data_field(self) -> Any:  # pragma: no cover
        """
        The field used for the payload body.

        This builds a model for the required data field. Validates the type of encoding
        being passed and builds a model if a datastructure is evaluated.
        """
        data_field = get_data_field(self)
        return data_field
