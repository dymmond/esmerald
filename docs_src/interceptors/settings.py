from typing import TYPE_CHECKING, List

from esmerald import EsmeraldSettings

from .myapp.interceptors import RequestParamInterceptor

if TYPE_CHECKING:
    from esmerald.core.interceptors.types import Interceptor


class AppSettings(EsmeraldSettings):
    def interceptors(self) -> List[Interceptor]:
        """
        Loads the default interceptors from the settings.
        """
        return [RequestParamInterceptor]
