from esmerald import EsmeraldSettings


# Create a ChildEsmeraldSettings object
class InstanceSettings(EsmeraldSettings):
    app_name: str = "my instance"
