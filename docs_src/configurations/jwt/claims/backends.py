from datetime import datetime
from typing import Any, Dict

from accounts.models import User
from edgy.exceptions import ObjectNotFound
from jose import JWSError, JWTError
from pydantic import BaseModel

from esmerald.conf import settings
from esmerald.exceptions import AuthenticationError, NotAuthorized
from esmerald.security.jwt.token import Token


class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    """
    Model used only to refresh
    """

    refresh_token: str


class TokenAccess(AccessToken, RefreshToken):
    """
    Model representation of an access token.
    """

    ...


class LoginIn(BaseModel):
    email: str
    password: str


class BackendAuthentication(BaseModel):
    """
    Utility class that helps with the authentication process.
    """

    email: str
    password: str

    async def authenticate(self) -> Dict[str, str]:
        """Authenticates a user and returns
        a dictionary containing the `access_token` and `refresh_token`
        in the format of:

        {
            "access_token": ...,
            "refresh_token": ...
        }
        """
        try:
            user: User = await User.query.get(email=self.email)
        except ObjectNotFound:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            await User().set_password(self.password)
        else:
            is_password_valid = await user.check_password(self.password)
            if is_password_valid and self.is_user_able_to_authenticate(user):
                # The lifetime of a token should be short, let us make 5 minutes.
                # You can use also the access_token_lifetime from the JWT config directly
                access_time = datetime.now() + settings.jwt_config.access_token_lifetime
                refresh_time = datetime.now() + settings.jwt_config.refresh_token_lifetime
                access_token = TokenAccess(
                    access_token=self.generate_user_token(
                        user,
                        time=access_time,
                        token_type=settings.jwt_config.access_token_name,  # 'access_token'
                    ),
                    refresh_token=self.generate_user_token(
                        user,
                        time=refresh_time,
                        token_type=settings.jwt_config.refresh_token_name,  # 'refresh_token'
                    ),
                )
                return access_token.model_dump()
            else:
                raise NotAuthorized(detail="Invalid credentials.")

    def is_user_able_to_authenticate(self, user: Any):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)

    def generate_user_token(self, user: User, token_type: str, time: datetime = None):
        """
        Generates the JWT token for the authenticated user.
        """
        if not time:
            later = datetime.now() + settings.jwt_config.access_token_lifetime
        else:
            later = time

        token = Token(sub=str(user.id), exp=later)
        return token.encode(
            key=settings.jwt_config.signing_key,
            algorithm=settings.jwt_config.algorithm,
            token_type=token_type,
        )


class RefreshAuthentication(BaseModel):
    """
    Refreshes the access token given a refresh token of a given user.

    This object does not perform any DB action, instead, uses the existing refresh
    token to generate a new access.
    """

    token: RefreshToken

    async def refresh(self) -> AccessToken:
        """
        Retrieves the header default of the config and validates against the decoding.
        Raises Authentication error if invalid.
        """
        token = self.token.refresh_token

        try:
            token = Token.decode(
                token=token,
                key=settings.jwt_config.signing_key,
                algorithms=[settings.jwt_config.algorithm],
            )
        except (JWSError, JWTError) as e:
            raise AuthenticationError(str(e)) from e

        if token.token_type != settings.jwt_config.refresh_token_name:
            raise NotAuthorized(detail="Only refresh tokens are allowed.")

        # Apply the maximum living time
        expiry_date = datetime.now() + settings.jwt_config.access_token_lifetime

        # New token object
        new_token = Token(sub=token.sub, exp=expiry_date)

        # Encode the token
        access_token = new_token.encode(
            key=settings.jwt_config.signing_key,
            algorithm=settings.jwt_config.algorithm,
            token_type=settings.jwt_config.access_token_name,
        )

        return AccessToken(access_token=access_token)
