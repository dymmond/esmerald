from typing import List, Union

from myapp.encoders import AttrsEncoder

from ravyn import RavynSettings
from ravyn.encoders import Encoder


class AppSettings(RavynSettings):
    @property
    def encoders(self) -> Union[List[Encoder], None]:
        return [AttrsEncoder]
