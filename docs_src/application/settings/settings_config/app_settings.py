from typing import TYPE_CHECKING

from esmerald import EsmeraldAPISettings

if TYPE_CHECKING:
    pass

# Create a ChildEsmeraldSettings object
class InstanceSettings(EsmeraldAPISettings):
    app_name: str = "my instance"
