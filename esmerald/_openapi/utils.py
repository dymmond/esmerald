import http.client
from typing import Any, Dict

from starlette import status

from esmerald._openapi.constants import REF_PREFIX


def parse_request(field_names: Any) -> Dict[str, Any]:
    """
    get json spec
    """

    schema = {}
    if len(field_names) == 1:
        for key, value in field_names[0].items():
            schema["application/json"] = {"schema": {"$ref": REF_PREFIX + value}}
    else:
        refs = {}
        for model in field_names:
            for k, v in model.items():
                refs[k] = {"$ref": REF_PREFIX + v}

        schema = {"application/json": {"schema": {"type": "object", "properties": refs}}}
    return {"content": schema}


def parse_resp(func: Any):
    """
    get the response spec

    If this function does not have explicit ``resp`` but have other models,
    a ``422 Validation Error`` will be append to the response spec. Since
    this may be triggered in the validation step.
    """
    responses = {}

    if func.responses:
        for status_code, response in func.responses.items():
            assert isinstance(response, dict), "An additional response must be a dict"
            additional_response = http.client.responses.get(status_code)
            description = response.get("description") or additional_response
            responses[str(status_code).upper()] = {"description": description}

    http422 = str(status.HTTP_422_UNPROCESSABLE_ENTITY)
    responses[http422] = {
        "content": {"application/json": {"schema": {"$ref": REF_PREFIX + "HTTPValidationError"}}},
    }
    return responses
