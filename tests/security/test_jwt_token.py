from datetime import datetime

from freezegun import freeze_time

from ravyn.security.jwt.token import Token


@freeze_time("2022-03-03")
def test_token_expiry():
    date = datetime.now()

    token = Token(exp=date)

    assert token.exp == date
