from typing import TYPE_CHECKING, List

from esmerald import EsmeraldAPISettings

from .myapp.interceptors import RequestParamInterceptor

if TYPE_CHECKING:
    from esmerald.core.interceptors.types import Interceptor


class AppSettings(EsmeraldAPISettings):
    def interceptors(self) -> List[Interceptor]:
        """
        Loads the default interceptors from the settings.
        """
        return [RequestParamInterceptor]
