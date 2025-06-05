from esmerald import ChildEsmerald, Esmerald, EsmeraldSettingsnclude


# Create a ChildEsmeraldSettings object
class ChildEsmeraldSettings(EsmeraldSettings):
    app_name: str = "child app"
    secret_key: str = "a child secret"


# Create a ChildEsmerald application
child_app = ChildEsmerald(routes=[...], settings_module=ChildEsmeraldSettings)

# Create an Esmerald application
app = Esmerald(routes=[Include("/child", app=child_app)])
