from esmerald import EsmeraldAPISettings


# Create a ChildEsmeraldSettings object
class InstanceSettings(EsmeraldAPISettings):
    app_name: str = "my instance"
