from esmerald.contrib.auth.tortoise.base_user import User as BaseUser
from tortoise import fields, models


class User(BaseUser):
    ...


class Profile(models.Model):
    """
    A profile is usually associated with a user in a 1:1 relationship.
    """

    user = fields.OneToOneField(
        "User", related_name="user", on_delete=fields.CASCADE, null=False
    )
    profile_type = fields.Charfield()
    role = fields.CharField()

    def __str__(self):
        return f"{self.user.email} - {self.profile_type}"
