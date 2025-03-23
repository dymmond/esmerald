from typing import Any, Callable, List, Optional, Sequence, Union

from pydantic.fields import AliasChoices, AliasPath

from esmerald import params
from esmerald.typing import Undefined
from esmerald.utils.enums import EncodingType

_PyUndefined: Any = Undefined


def Security(
    dependency: Optional[Callable[..., Any]] = None,
    *,
    scopes: Optional[Sequence[str]] = None,
    use_cache: bool = True,
) -> params.Security:
    """
    This function should be only called if Inject/Injects is not used in the dependencies.
    This is a simple wrapper of the classic Inject().
    """
    return params.Security(dependency=dependency, scopes=scopes, use_cache=use_cache)


def Requires(
    dependency: Optional[Callable[..., Any]] = None,
    *,
    use_cache: bool = True,
) -> Any:
    """
    This function should be only called if Inject/Injects is not used in the dependencies.
    This is a simple wrapper of the classic Depends().
    """
    return params.Requires(dependency=dependency, use_cache=use_cache)


def Form(
    default: Any = _PyUndefined,
    *,
    annotation: Optional[Any] = None,
    default_factory: Optional[Callable[..., Any]] = _PyUndefined,
    allow_none: Optional[bool] = True,
    media_type: Union[str, EncodingType] = EncodingType.URL_ENCODED,
    content_encoding: Optional[str] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = _PyUndefined,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    examples: Optional[List[Any]] = None,
    validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
    discriminator: Optional[str] = None,
    max_digits: Optional[int] = _PyUndefined,
    strict: Optional[bool] = _PyUndefined,
    frozen: Optional[bool] = None,
    validate_default: bool = True,
    init_var: bool = True,
    kw_only: bool = True,
    include_in_schema: bool = True,
) -> Any:
    return params.Form(
        default=default,
        annotation=annotation,
        default_factory=default_factory,
        allow_none=allow_none,
        media_type=media_type,
        content_encoding=content_encoding,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        examples=examples,
        validation_alias=validation_alias,
        discriminator=discriminator,
        max_digits=max_digits,
        strict=strict,
        frozen=frozen,
        validate_default=validate_default,
        init_var=init_var,
        kw_only=kw_only,
        include_in_schema=include_in_schema,
    )
