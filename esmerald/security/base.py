from lilya.contrib.security.base import SecurityScheme as LilyaSecurityScheme


class SecurityBase(LilyaSecurityScheme):
    scheme_name: str | None = None
    """
    An optional name for the security scheme.
    """
    __auto_error__: bool = False
    """
    A flag to indicate if automatic error handling should be enabled.
    """
    __is_security__: bool = True
    """A flag to indicate that this is a security scheme. """


class HttpSecurityBase(LilyaSecurityScheme):
    scheme_name: str | None = None
    """
    An optional name for the security scheme.
    """
    realm: str | None = None
    """
    An optional realm for the security scheme.
    """
    __auto_error__: bool = False
    """
    A flag to indicate if automatic error handling should be enabled.
    """
