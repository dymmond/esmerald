from typing import List, Union

from myapp.encoders import AttrsEncoder

from esmerald import EsmeraldAPISettings
from esmerald.encoders import Encoder


class AppSettings(EsmeraldAPISettings):
    @property
    def encoders(self) -> Union[List[Encoder], None]:
        return [AttrsEncoder]
