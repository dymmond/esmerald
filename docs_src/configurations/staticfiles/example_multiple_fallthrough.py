from pathlib import Path

from esmerald import Esmerald, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static",
    directory=["static/overwrites", "static", "static/defaults", "node_modules"],
    name="static",
)

app = Esmerald(static_files_config=static_files_config)
