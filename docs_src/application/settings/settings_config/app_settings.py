from ravyn import RavynSettings


# Create a ChildRavynSettings object
class InstanceSettings(RavynSettings):
    app_name: str = "my instance"
