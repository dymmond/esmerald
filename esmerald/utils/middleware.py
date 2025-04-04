from __future__ import annotations

from typing import Any, cast

from lilya.middleware.base import DefineMiddleware


def wrap_middleware(middleware: DefineMiddleware | str | Any, **kwargs: Any) -> DefineMiddleware:
    """
    Wraps a middleware input into a `DefineMiddleware` instance, ensuring consistent middleware usage.

    This utility function is designed to accept a middleware in various formats—either as an already
    instantiated `DefineMiddleware`, a string path to a middleware class, or a raw class/function reference—
    and normalize it into a `DefineMiddleware` object. This allows for flexible middleware registration
    while maintaining a consistent internal representation.

    ### Parameters
    ----------
    middleware : DefineMiddleware | str | Any
        The middleware to wrap. This can be:
        - An instance of `DefineMiddleware`, which will be returned directly.
        - A string representing the import path of a middleware class/function.
        - A class or function that implements the ASGI middleware interface.

    **kwargs : Any
        Additional keyword arguments to be passed to the `DefineMiddleware` constructor if the
        middleware is not already a `DefineMiddleware` instance.

    ### Returns
    -------
    DefineMiddleware
        A properly instantiated `DefineMiddleware` object representing the middleware.
        If the input is already an instance, it is returned as-is. Otherwise, a new instance is created
        using the given middleware and any additional keyword arguments.

    ### Example
    -------
    >>> from lilya.middleware.base import DefineMiddleware
    >>> class MyMiddleware:
    ...     def __init__(self, app):
    ...         self.app = app
    ...     async def __call__(self, scope, receive, send):
    ...         await self.app(scope, receive, send)

    >>> wrap_middleware(MyMiddleware, some_arg="value")
    DefineMiddleware(MyMiddleware, some_arg="value")

    >>> wrap_middleware("myproject.middleware.MyMiddleware", some_arg="value")
    DefineMiddleware("myproject.middleware.MyMiddleware", some_arg="value")

    >>> already_wrapped = DefineMiddleware(MyMiddleware)
    >>> wrap_middleware(already_wrapped) is already_wrapped
    True
    """
    if isinstance(middleware, DefineMiddleware):
        return middleware
    return DefineMiddleware(cast(Any, middleware), **kwargs)
