from typing import Union

from ravyn.security.jwt.token import Token as RavynToken


class Token(RavynToken):
    token_type: Union[str, None] = None
