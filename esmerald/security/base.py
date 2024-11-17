from typing import Optional

from esmerald.openapi.models import (
    SecurityScheme,
)


class SecurityBase(SecurityScheme):
    scheme_name: Optional[str] = None
    """
    An optional name for the security scheme.
    """
    __auto_error__: bool = False
    """
    A flag to indicate if automatic error handling should be enabled.
    """
