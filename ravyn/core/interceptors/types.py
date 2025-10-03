from typing import Type, TypeVar, Union

from ravyn.core.interceptors.interceptor import EsmeraldInterceptor

EsmeraldInterceptorType = TypeVar("EsmeraldInterceptorType", bound=EsmeraldInterceptor)
Interceptor = Union[Type[EsmeraldInterceptorType], Type[EsmeraldInterceptor]]
