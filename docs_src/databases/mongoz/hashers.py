from typing import List

from esmerald import EsmeraldAPISettings
from esmerald.contrib.auth.hashers import BcryptPasswordHasher


class CustomHasher(BcryptPasswordHasher):
    """
    All the hashers inherit from BasePasswordHasher
    """

    salt_entropy = 3000


class MySettings(EsmeraldAPISettings):
    @property
    def password_hashers(self) -> List[str]:
        return ["myapp.hashers.CustomHasher"]
