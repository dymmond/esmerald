import http.client
import inspect
import warnings
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Type, Union, cast

from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from typing_extensions import Literal

from esmerald._openapi._utils import (
    status_code_ranges,
    validation_error_definition,
    validation_error_response_definition,
)
from esmerald._openapi.constants import METHODS_WITH_BODY, REF_PREFIX, REF_TEMPLATE
from esmerald._openapi.models import OpenAPI
from esmerald.params import Body, Param
from esmerald.responses import Response
from esmerald.typing import ModelMap, Undefined
