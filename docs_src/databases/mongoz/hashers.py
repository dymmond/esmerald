from typing import List

from ravyn import RavynSettings
from ravyn.contrib.auth.hashers import BcryptPasswordHasher


class CustomHasher(BcryptPasswordHasher):
    """
    All the hashers inherit from BasePasswordHasher
    """

    salt_entropy = 3000


class MySettings(RavynSettings):
    @property
    def password_hashers(self) -> List[str]:
        return ["myapp.hashers.CustomHasher"]
