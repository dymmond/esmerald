from esmerald import CORSConfig, EsmeraldSettings


class CustomSettings(EsmeraldSettings):
    @property
    def cors_config(self) -> CORSConfig:
        """
        Initial Default configuration for the CORS.
        This can be overwritten in another setting or simply override
        `allow_origins` or then override the `def cors_config()`
        property to change the behavior of the whole cors_config.
        """
        if not self.allow_origins:
            return None
        return CORSConfig(allow_origins=self.allow_origins, allow_methods=["*"])
