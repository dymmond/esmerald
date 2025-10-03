from ravyn import CSRFConfig, RavynSettings, ImproperlyConfigured


class CustomSettings(RavynSettings):
    @property
    def csrf_config(self) -> CSRFConfig:
        """
        Initial Default configuration for the CSRF.
        This can be overwritten in another setting or simply override `secret`
        or then override the `def csrf_config()` property to change the behavior
        of the whole csrf_config.
        """
        if not self.secret_key:
            raise ImproperlyConfigured("`secret` setting not configured.")
        return CSRFConfig(secret=self.secret_key)
