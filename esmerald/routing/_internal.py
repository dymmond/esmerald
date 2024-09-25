import inspect
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Union, _GenericAlias, cast, get_args

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from esmerald.encoders import ENCODER_TYPES, is_body_encoder
from esmerald.enums import EncodingType
from esmerald.openapi.params import ResponseParam
from esmerald.params import Body
from esmerald.utils.constants import DATA, PAYLOAD
from esmerald.utils.models import create_field_model

if TYPE_CHECKING:
    from esmerald.routing.router import HTTPHandler, WebhookHandler


def get_base_annotations(base_annotation: Any) -> Dict[str, Any]:
    """
    Returns the annotations of the base class.

    Args:
        base (Any): The base class.

    Returns:
        Dict[str, Any]: The annotations of the base class.
    """
    base_annotations: Dict[str, Any] = {}
    for base in base_annotation.__bases__:
        base_annotations.update(**get_base_annotations(base))
        if hasattr(base, "__annotations__"):
            for name, annotation in base.__annotations__.items():
                base_annotations[name] = annotation
    return base_annotations


def convert_annotation_to_pydantic_model(field_annotation: Any) -> Any:
    """
    Converts any annotation of the body into a Pydantic
    base model.

    This is used for OpenAPI representation purposes only.

    Esmerald will try internally to convert the model into a Pydantic BaseModel,
    this will serve as representation of the model in the documentation but internally,
    it will use the native type to validate the data being sent and parsed in the
    payload/data field.

    Encoders are not supported in the OpenAPI representation, this is because the encoders
    are unique to Esmerald and are not part of the OpenAPI specification. This is why
    we convert the encoders into a Pydantic model for OpenAPI representation purposes only.
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

        # Get any possible annotations from the base classes
        # This can be useful for inheritance with custom encoders
        base_annotations: Dict[str, Any] = {**get_base_annotations(field_annotation)}
        field_annotations = {
            **base_annotations,
            **field_annotation.__annotations__,
        }
        for name, annotation in field_annotations.items():
            field_definitions[name] = (annotation, ...)
        return create_model(
            field_annotation.__name__,
            __config__={"arbitrary_types_allowed": True},
            **field_definitions,
        )
    return field_annotation


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
        body.annotation = convert_annotation_to_pydantic_model(body.annotation)

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


def get_complex_data_field(
    handler: Union["HTTPHandler", "WebhookHandler", Any], fields: Dict[str, FieldInfo]
) -> Any:  # pragma: no cover
    """
    The field used for the payload body.

    This builds a model for the required data field. Validates the type of encoding
    being passed and builds a model if a datastructure is evaluated.
    """
    body_fields_set = set()
    body_fields: Dict[str, FieldInfo] = {}

    for name, field in fields.items():
        if name in body_fields_set:
            continue

        body_fields_set.add(name)
        body_fields[name] = field

    # Set the field definitions
    field_definitions = {}
    for name, param in body_fields.items():
        param.annotation = convert_annotation_to_pydantic_model(param.annotation)
        field_definitions[name] = param.annotation, ...

    # Create the model from the field definitions
    model = create_model(  # type: ignore
        "DataField", __config__={"arbitrary_types_allowed": True}, **field_definitions
    )
    # Create the body field
    body = Body(annotation=model, title=f"Body_{handler.operation_id}")

    # Check the annotation type
    if not body.title:
        body.title = f"Body_{handler.operation_id}"
    return body


def get_data_field(handler: Union["HTTPHandler", "WebhookHandler", Any]) -> Any:
    """
    Retrieves the data field from the given handler.

    Args:
        handler (Union[HTTPHandler, WebhookHandler, Any]): The handler object.

    Returns:
        Any: The data field.

    Raises:
        None

    This function checks if the handler has any body encoder fields. If there are less than 2 body encoder fields,
    it calls the get_original_data_field function. Otherwise, it calls the get_complex_data_field function.

    One the steps is to make sure backwards compatibility and this means to make sure previous
    versions of Esmerald are supported the way they are supposed to.

    The other thing is to make sure we extract any value from the signature of the handler and
    match against any encoder, custom or default, and isolate them as body fields and then extract
    the values that are not in the dependencies since those are not considered part of the body
    but as dependency itself.

    If the body fields are less than 1 and using the reserved `data` or `payload` then it will
    default to the normal Esmerald processing, otherwise it will use the complex approach of
    designing the OpenAPI body.
    """
    is_data_or_payload = (
        DATA
        if DATA in handler.signature_model.model_fields
        else (PAYLOAD if PAYLOAD in handler.signature_model.model_fields else None)
    )

    # If there are no body fields, we simply return the original
    # default Esmerald body parsing
    if not handler.body_encoder_fields:
        return get_original_data_field(handler)

    if len(handler.body_encoder_fields) < 2 and is_data_or_payload is not None:
        return get_original_data_field(handler)
    return get_complex_data_field(handler, fields=handler.body_encoder_fields)


class OpenAPIFieldInfoMixin:
    """
    Used for validating model fields necessary for the
    OpenAPI parsing only.

    Don't use this anywhere else.
    """

    @property
    def body_encoder_fields(self) -> Dict[str, FieldInfo]:
        """
        The fields that are body encoders.

        This is used for OpenAPI representation purposes only.
        """
        # Making sure the dependencies are not met as body fields for OpenAPI representation
        handler_dependencies = set(self.get_dependencies().keys())

        # Getting everything else that is not considered a dependency
        body_encoder_fields = {
            name: field
            for name, field in self.signature_model.model_fields.items()
            if is_body_encoder(field.annotation) and name not in handler_dependencies
        }
        return body_encoder_fields

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
