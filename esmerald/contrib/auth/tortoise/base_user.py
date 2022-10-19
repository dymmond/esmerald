from tortoise import fields
from tortoise.models import Model

from esmerald.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)


class AutoIncrementIntMixin(Model):
    """
    Auto increment for integers.
    """

    id = fields.IntField(pk=True)

    class Meta:
        ordering = ["-id"]
        abstract = True


class AutoIncrementBigIntMixin(Model):
    """
    Auto increment for big integers.
    """

    id = fields.BigIntField(pk=True)

    class Meta:
        ordering = ["-id"]
        abstract = True


class AbstractUser(Model):
    """
    Base model used for a custom model of an application contains.
    """

    first_name = fields.CharField(description="First name", max_length=150)
    last_name = fields.CharField(description="Last name", max_length=150)
    username = fields.CharField(description="Username", max_length=150, unique=True)
    email = fields.CharField(description="Email address", max_length=120, unique=True)
    password = fields.CharField(description="Password", max_length=128)
    last_login = fields.DatetimeField(description="Last login", null=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    class Meta:
        abstract = True

    @property
    async def is_authenticated(self):
        """
        Always return True.
        """
        return True

    async def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password
        await self.save()

    async def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        async def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            await self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    async def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    async def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    @classmethod
    async def _create_user(cls, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        user = cls(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        await user.save()
        return user

    @classmethod
    async def create_user(cls, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await cls._create_user(username, email, password, **extra_fields)

    @classmethod
    async def create_superuser(cls, username, email=None, password=None, **extra_fields):
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
