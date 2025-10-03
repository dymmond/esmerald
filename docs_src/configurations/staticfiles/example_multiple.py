from pathlib import Path

from ravyn import Ravyn, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static",
    packages=["mypackage"],
    directory=Path("static"),
    name="static",
)

static_files_node_modules_config = StaticFilesConfig(
    path="/static/node_modules", directory=Path("node_modules"), name="static"
)

app = Ravyn(static_files_config=[static_files_node_modules_config, static_files_config])
