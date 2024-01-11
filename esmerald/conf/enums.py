from enum import Enum


class EnvironmentType(str, Enum):
    """An Enum for environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
