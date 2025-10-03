from ravyn import ChildRavyn, Ravyn, EsmeraldSettingsnclude


# Create a ChildRavynSettings object
class ChildRavynSettings(RavynSettings):
    app_name: str = "child app"
    secret_key: str = "a child secret"


# Create a ChildRavyn application
child_app = ChildRavyn(routes=[...], settings_module=ChildRavynSettings)

# Create an Ravyn application
app = Ravyn(routes=[Include("/child", app=child_app)])
