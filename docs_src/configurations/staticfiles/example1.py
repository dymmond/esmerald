from esmerald import Esmerald, StaticFilesConfig

static_files_config = StaticFilesConfig(
    path="/static", packages=["mypackage"], directory="/static"
)

app = Esmerald(static_files_config=static_files_config)
