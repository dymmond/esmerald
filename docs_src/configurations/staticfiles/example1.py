from esmerald import Esmerald, StaticFilesConfig

from pathlib import Path

static_files_config = StaticFilesConfig(
    path="/static", packages=["mypackage"], directory=Path("static")
)

app = Esmerald(static_files_config=static_files_config)
