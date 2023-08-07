from datetime import datetime
from typing import Any

import edgy

from esmerald.contrib.auth.hashers import check_password, is_password_usable, make_password


class AbstractUser(edgy.Model):
    """
    Base model used for a custom user of any application.
    """

    first_name: str = edgy.CharField(max_length=150)
    last_name: str = edgy.CharField(max_length=150)
    username: str = edgy.CharField(max_length=150, unique=True)
    email: str = edgy.EmailField(max_length=120, unique=True)
    password: str = edgy.CharField(max_length=128)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)  # type: ignore
    is_staff: bool = edgy.BooleanField(default=False)  # type: ignore
    is_superuser: bool = edgy.BooleanField(default=False)  # type: ignore

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    class Meta:
        abstract = True

    @property
    async def is_authenticated(self) -> bool:
        """
        Always return True.
        """
        return True

    async def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)
        self._password = raw_password
        await self.update(password=make_password(raw_password))

    async def check_password(self, raw_password: str) -> bool:
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        async def setter(raw_password: str) -> None:
            await self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            await self.update(password=self.password)

        return check_password(raw_password, str(self.password), setter)

    async def set_unusable_password(self) -> None:
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    async def has_usable_password(self) -> bool:
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    @classmethod
    async def _create_user(
        cls, username: str, email: str, password: str, **extra_fields: Any
    ) -> "AbstractUser":
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        password = make_password(password)
        user: AbstractUser = await cls.query.create(
            username=username, email=email, password=password, **extra_fields
        )
        return user

    @classmethod
    async def create_user(
        cls,
        username: str,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> "AbstractUser":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await cls._create_user(username, email, password, **extra_fields)

    @classmethod
    async def create_superuser(
        cls,
        username: str,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> "AbstractUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await cls._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Implementation of the Abstract user and can be used directly.
    """

    ...
