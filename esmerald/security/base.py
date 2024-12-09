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
    __is_security__: bool = True
    """A flag to indicate that this is a security scheme. """


class HttpSecurityBase(SecurityScheme):
    scheme_name: Optional[str] = None
    """
    An optional name for the security scheme.
    """
    realm: Optional[str] = None
    """
    An optional realm for the security scheme.
    """
    __auto_error__: bool = False
    """
    A flag to indicate if automatic error handling should be enabled.
    """
