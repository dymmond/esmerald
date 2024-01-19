from typing import Union

from esmerald.security.jwt.token import Token as EsmeraldToken


class Token(EsmeraldToken):
    token_type: Union[str, None] = None
