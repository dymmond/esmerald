from __future__ import annotations

try:
    from a2wsgi.wsgi import WSGIMiddleware as WSGIMiddleware  # noqa
except ModuleNotFoundError:
    raise RuntimeError(
        "You need to install the package `a2wsgi` to be able to use this middleware. "
        "Simply run `pip install a2wsgi`."
    ) from None


__all__ = ["WSGIMiddleware"]
