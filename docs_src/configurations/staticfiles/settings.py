from esmerald import EsmeraldAPISettings, StaticFilesConfig


class CustomSettings(EsmeraldAPISettings):
    @property
    def static_files_config(self) -> StaticFilesConfig:
        """
        Simple configuration indicating where the statics will be placed in
        the application.
        """
        return StaticFilesConfig(path="/static", packages=["mypackage"], directory="/static")
