from typing import List, Union

from myapp.encoders import AttrsEncoder

from esmerald import EsmeraldSettings
from esmerald.encoders import Encoder


class AppSettings(EsmeraldSettings):
    @property
    def encoders(self) -> Union[List[Encoder], None]:
        return [AttrsEncoder]
