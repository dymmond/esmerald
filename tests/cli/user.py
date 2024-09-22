from typing import Any

import edgy
import pytest

from esmerald.conf import settings

models = settings.edgy_registry
pytestmark = pytest.mark.anyio


class User(edgy.Model):
    """
    Base model used for a custom user of any application.
    """

    first_name = edgy.CharField(max_length=150)
    last_name = edgy.CharField(max_length=150)
    username = edgy.CharField(max_length=150, unique=True)
    email = edgy.EmailField(max_length=120, unique=True)
    password = edgy.CharField(max_length=128)
    last_login = edgy.DateTimeField(null=True)
    is_active = edgy.BooleanField(default=True)
    is_staff = edgy.BooleanField(default=False)
    is_superuser = edgy.BooleanField(default=False)

    class Meta:
        registry = models

    @classmethod
    async def create_superuser(
        cls,
        username: str,
        email: str,
        password: str,
        **extra_fields: Any,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return await cls._create_user(username, email, password, **extra_fields)

    @classmethod
    async def _create_user(cls, username: str, email: str, password: str, **extra_fields: Any):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        user = await cls.query.create(
            username=username, email=email, password=password, **extra_fields
        )
        return user
