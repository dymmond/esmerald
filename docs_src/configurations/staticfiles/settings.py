from pathlib import Path

from ravyn import RavynSettings, StaticFilesConfig


class CustomSettings(RavynSettings):
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
