from typing import List

from esmerald import EsmeraldSettings
from esmerald.contrib.auth.hashers import BcryptPasswordHasher


class CustomHasher(BcryptPasswordHasher):
    """
    All the hashers inherit from BasePasswordHasher
    """

    salt_entropy = 3000


class MySettings(EsmeraldSettings):
    @property
    def password_hashers(self) -> List[str]:
        return ["myapp.hashers.CustomHasher"]
