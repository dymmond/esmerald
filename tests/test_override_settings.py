import pytest

from esmerald.conf import settings
from esmerald.testclient import override_settings


@override_settings(environment="test_func")
def test_can_override_settings():
    assert settings.environment == "test_func"


@override_settings(environment="test_func")
def test_name_of_settings():
    assert settings.__class__.__name__ == "TestSettings"


class TestInClass:
    @override_settings(environment="test_func")
    def test_can_override_settings(self):
        assert settings.environment == "test_func"

    @override_settings(environment="test_func")
    def test_name_of_settings(self):
        assert settings.__class__.__name__ == "TestSettings"


class TestInClassAsync:
    @override_settings(environment="test_func")
    @pytest.mark.asyncio
    async def test_can_override_settings(self, test_client_factory):
        assert settings.environment == "test_func"

    @override_settings(environment="test_func")
    @pytest.mark.asyncio
    async def test_name_of_settings(self, test_client_factory):
        assert settings.__class__.__name__ == "TestSettings"
