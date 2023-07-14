from functools import cached_property
from typing import Any, Dict, List

from pydantic import BaseModel

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

        The response models can be a list representation or a single object representation.
        If another type of object is passed through the `model`, an Assertation error is raised.
        """
        responses: Dict[int, ResponseParam] = {}
        if self.responses:
            for status_code, response in self.responses.items():
                assert isinstance(response.model, list) or issubclass(
                    response.model, BaseModel
                ), "The model must be a list or a single model."

                if isinstance(response.model, list) and len(response.model) > 1:
                    raise AssertionError(
                        "The representation of a list of models in OpenAPI can only be one."
                    )

                annotation = (
                    List[response.model[0]] if isinstance(response.model, list) else response.model
                )

                name = (
                    response.model[0].__name__
                    if isinstance(response.model, list)
                    else response.model.__name__
                )

                responses[status_code] = ResponseParam(
                    annotation=annotation,
                    description=response.description,
                    alias=name,
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
