from functools import cached_property
from typing import Any, Dict

from esmerald.openapi.params import ResponseParam
from esmerald.params import Body
from esmerald.utils.constants import DATA


class FieldInfoMixin:
    """
    Used for validating model fields necessary for the
    OpenAPI parsing.
    """

    @cached_property
    def response_models(self) -> Dict[int, Any]:
        """
        The models converted into pydantic fields with the model used for OpenAPI.
        """
        responses: Dict[int, ResponseParam] = {}
        if self.responses:
            for status_code, response in self.responses.items():
                responses[status_code] = ResponseParam(
                    annotation=response.model,
                    description=response.description,
                    alias=response.model.__name__,
                )
        return responses

    @cached_property
    def data_field(self) -> Any:
        """The field used for the payload body"""
        if DATA in self.signature_model.model_fields:
            data = self.signature_model.model_fields[DATA]

            body = Body(alias="body")
            for key, _ in data._attributes_set.items():
                setattr(body, key, getattr(data, key, None))
            return body
