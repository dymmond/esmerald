from typing import Union

from ravyn.security.jwt.token import Token as RavynAPIExceptionToken


class Token(RavynAPIExceptionToken):
    token_type: Union[str, None] = None
