from pathlib import Path

from esmerald import Esmerald, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static", packages=["mypackage"], directory=Path("static"), name="static"
)

app = Esmerald(static_files_config=static_files_config)
