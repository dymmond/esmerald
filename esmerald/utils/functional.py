import copy
import operator
from typing import Any, Callable, TypeVar

empty = object()
RT = TypeVar("RT")  # return type


def new_method_proxy(func: Callable[..., RT]) -> Callable[..., RT]:
    def inner(self, *args: Any) -> RT:  # type: ignore
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)

    inner._mask_wrapped = False
    return inner


class LazyObject:  # pragma: no cover
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.
    By subclassing, you have the opportunity to intercept and alter the
    instantiation. If you don't need to do that, use SimpleLazyObject.

    Based on Django and this article: https://coderbook.com/python/2020/04/23/how-to-make-lazy-python.html
    """

    _wrapped = None

    def __init__(self) -> None:
        self._wrapped = empty

    def __getattribute__(self, name: str) -> Any:
        if name == "_wrapped":
            return super().__getattribute__(name)
        value: Any = super().__getattribute__(name)
        if not getattr(value, "_mask_wrapped", True):
            raise AttributeError
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_wrapped":
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name: str) -> None:
        if name == "_wrapped":
            raise TypeError("Can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self) -> Any:
        """
        Must be implemented by subclasses to initialize the wrapped object.
        """
        raise NotImplementedError("subclasses of LazyObject must provide a _setup() method")

    def __reduce__(self) -> Any:
        if self._wrapped is empty:
            self._setup()
        return (unpickle_lazyobject, (self._wrapped,))

    def __copy__(self) -> Any:
        if self._wrapped is empty:
            return type(self)()
        else:
            return copy.copy(self._wrapped)

    def __deepcopy__(self, memo: Any) -> Any:
        if self._wrapped is empty:
            result = type(self)()
            memo[id(self)] = result
            return result

    __getattr__ = new_method_proxy(getattr)
    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)
    __dir__ = new_method_proxy(dir)
    __hash__ = new_method_proxy(hash)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))  # type: ignore
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __gt__ = new_method_proxy(operator.gt)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


def unpickle_lazyobject(wrapped: Any) -> Any:  # pragma: no cover
    """
    Used to unpickle lazy objects. Just return its argument, which will be the
    wrapped object.
    """
    return wrapped


class SimpleLazyObject(LazyObject):  # pragma: no cover
    """
    A lazy object initialized from any function.
    Designed for compound objects of unknown type.
    """

    def __init__(self, func: Callable[..., RT]) -> None:
        """
        Pass in a callable that returns the object to be wrapped.
        If copies are made of the resulting SimpleLazyObject, which can happen
        in various circumstances, then you must ensure that the
        callable can be safely run more than once and will return the same
        value.
        """
        self.__dict__["_setupfunc"] = func
        super().__init__()

    def _setup(self) -> Any:
        self._wrapped = self._setupfunc()

    def __repr__(self) -> str:
        if self._wrapped is empty:
            repr_attr = self._setupfunc
        else:
            repr_attr = self._wrapped
        return "<{}: {!r}>".format(type(self).__name__, repr_attr)

    def __copy__(self) -> Any:
        if self._wrapped is empty:
            return SimpleLazyObject(self._setupfunc)
        else:
            # If initialized, return a copy of the wrapped object.
            return copy.copy(self._wrapped)

    def __deepcopy__(self, memo: Any) -> Any:
        if self._wrapped is empty:
            result = SimpleLazyObject(self._setupfunc)
            memo[id(self)] = result
            return result
        return copy.deepcopy(self._wrapped, memo)

    __add__ = new_method_proxy(operator.add)

    @new_method_proxy
    def __radd__(self, other: Any) -> Any:
        return other + self
