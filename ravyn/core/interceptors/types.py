from typing import Type, TypeVar, Union

from ravyn.core.interceptors.interceptor import RavynInterceptor

RavynInterceptorType = TypeVar("RavynInterceptorType", bound=RavynInterceptor)
Interceptor = Union[Type[RavynInterceptorType], Type[RavynInterceptor]]
