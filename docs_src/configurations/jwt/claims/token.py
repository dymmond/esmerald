from typing import Union

from ravyn.security.jwt.token import Token as EsmeraldToken


class Token(EsmeraldToken):
    token_type: Union[str, None] = None
