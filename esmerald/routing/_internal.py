from functools import cached_property
from typing import Any, Dict, List, cast, get_args

from esmerald.enums import EncodingType
from esmerald.openapi.params import ResponseParam
from esmerald.params import Body
from esmerald.utils.constants import DATA, PAYLOAD
from esmerald.utils.models import create_field_model


class FieldInfoMixin:
    """
    Used for validating model fields necessary for the
    OpenAPI parsing.
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
                    annotation=annotation,
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
        if (
            DATA in self.signature_model.model_fields
            or PAYLOAD in self.signature_model.model_fields
        ):
            data_or_payload = DATA if DATA in self.signature_model.model_fields else PAYLOAD
            data = self.signature_model.model_fields[data_or_payload]

            if not isinstance(data, Body):
                body = Body(alias="body")
                for key, _ in data._attributes_set.items():
                    setattr(body, key, getattr(data, key, None))
            else:
                body = data

            if not body.title:
                body.title = f"Body_{self.operation_id}"

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
