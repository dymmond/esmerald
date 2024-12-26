from pathlib import Path

from esmerald import Esmerald, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static",
    packages=["mypackage"],
    directory=Path("static"),
    name="static",
)

static_files_node_modules_config = StaticFilesConfig(
    path="/static/node_modules", directory=Path("node_modules"), name="static"
)

app = Esmerald(static_files_config=[static_files_node_modules_config, static_files_config])
