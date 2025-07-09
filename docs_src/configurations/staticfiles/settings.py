from pathlib import Path

from esmerald import EsmeraldSettings, StaticFilesConfig


class CustomSettings(EsmeraldSettings):
    @property
    def static_files_config(self) -> StaticFilesConfig:
        """
        Simple configuration indicating where the statics will be placed in
        the application.
        """
        return StaticFilesConfig(
            path="/static",
            packages=["mypackage"],
            directory=Path("static"),
            name="static",
        )
