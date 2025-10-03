from typing import TYPE_CHECKING, List

from ravyn import RavynSettings

from .myapp.interceptors import RequestParamInterceptor

if TYPE_CHECKING:
    from ravyn.core.interceptors.types import Interceptor


class AppSettings(RavynSettings):
    def interceptors(self) -> List[Interceptor]:
        """
        Loads the default interceptors from the settings.
        """
        return [RequestParamInterceptor]
