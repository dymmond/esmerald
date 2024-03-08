from enum import Enum


class BaseEnum(str, Enum):
    def __str__(self) -> str:
        return self.value  # type: ignore

    def __repr__(self) -> str:
        return str(self)


class EnvironmentType(BaseEnum):
    """
    An Enum for environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
