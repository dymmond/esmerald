from pathlib import Path

from ravyn import Ravyn, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static",
    directory=["static/overwrites", "static", "static/defaults", "node_modules"],
    name="static",
)

app = Ravyn(static_files_config=static_files_config)
