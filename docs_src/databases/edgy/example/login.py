from datetime import datetime, timedelta

from accounts.models import User
from edgy.exceptions import DoesNotFound
from pydantic import BaseModel

from ravyn import JSONResponse, post, status
from ravyn.conf import settings
from ravyn.security.jwt.token import Token


class LoginIn(BaseModel):
    email: str
    password: str


class BackendAuthentication(BaseModel):
    """
    Utility class that helps with the authentication process.
    """

    email: str
    password: str

    async def authenticate(self) -> str:
        """Authenticates a user and returns a JWT string"""
        try:
            user: User = await User.query.get(email=self.email)
        except DoesNotFound:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            await User().set_password(self.password)
        else:
            is_password_valid = await user.check_password(self.password)
            if is_password_valid and self.is_user_able_to_authenticate(user):
                # The lifetime of a token should be short, let us make 5 minutes.
                # You can use also the access_token_lifetime from the JWT config directly
                time = datetime.now() + settings.jwt_config.access_token_lifetime
                return self.generate_user_token(user, time=time)

    def is_user_able_to_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)

    def generate_user_token(self, user: User, time=None):
        """
        Generates the JWT token for the authenticated user.
        """
        if not time:
            later = datetime.now() + timedelta(minutes=20)
        else:
            later = time

        token = Token(sub=user.id, exp=later)
        return token.encode(
            key=settings.jwt_config.signing_key, algorithm=settings.jwt_config.algorithm
        )


@post(status_code=status.HTTP_200_OK, tags=["auth"])
async def login(data: LoginIn) -> JSONResponse:
    """
    Login a user and returns a JWT token, else raises ValueError
    """
    auth = BackendAuthentication(email=data.email, password=data.password)
    token = await auth.authenticate()
    return JSONResponse({settings.jwt_config.access_token_name: token})
