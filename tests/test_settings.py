from esmerald.conf import settings
from esmerald.testclient import create_client


def test_default_settings():

    with create_client([]) as client:
        assert client.app.settings.app_name == settings.app_name
        assert client.app.settings.environment == "testing"
        assert client.app.settings.debug == settings.debug
        assert client.app.settings.allowed_hosts == settings.allowed_hosts
        assert client.app.settings.enable_sync_handlers == settings.enable_sync_handlers
        assert client.app.settings.enable_openapi == settings.enable_openapi
        assert client.app.settings.allow_origins == settings.allow_origins
        assert client.app.settings.on_shutdown == settings.on_shutdown
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.lifespan == settings.lifespan
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.version == settings.version
        assert client.app.settings.secret_key == settings.secret_key
        assert client.app.settings.response_class == settings.response_class
        assert client.app.settings.response_cookies == settings.response_cookies
        assert client.app.settings.tags == settings.tags
        assert client.app.settings.include_in_schema == settings.include_in_schema
        assert client.app.settings.scheduler_class == settings.scheduler_class
        assert client.app.settings.reload == settings.reload
        assert client.app.settings.password_hashers == settings.password_hashers
        assert client.app.settings.csrf_config == settings.csrf_config
        assert client.app.settings.async_exit_config == settings.async_exit_config
        assert client.app.settings.template_config == settings.template_config
        assert client.app.settings.static_files_config == settings.static_files_config
        assert client.app.settings.cors_config == settings.cors_config
        assert client.app.settings.session_config == settings.session_config
        assert client.app.settings.openapi_config == settings.openapi_config
        assert client.app.settings.middleware == settings.middleware
        assert client.app.settings.permissions == settings.permissions
        assert client.app.settings.dependencies == settings.dependencies
        assert client.app.settings.exception_handlers == settings.exception_handlers
        assert client.app.settings.redirect_slashes == settings.redirect_slashes
