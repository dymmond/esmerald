from ravyn import RavynSettings, ImproperlyConfigured, SessionConfig


class CustomSettings(RavynSettings):
    @property
    def session_config(self) -> SessionConfig:
        """
        Initial Default configuration for the SessionConfig.
        This can be overwritten in another setting or simply override
        `session_config` or then override the `def session_config()`
        property to change the behavior of the whole session_config.
        """
        if not self.secret_key:
            raise ImproperlyConfigured("`secret` setting not configured.")
        return SessionConfig(
            secret_key=self.secret_key,
            session_cookie="session",
        )
