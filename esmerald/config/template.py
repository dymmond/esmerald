from typing import List, Type, Union

from pydantic import BaseModel, ConfigDict, DirectoryPath

from esmerald.protocols.template import TemplateEngineProtocol
from esmerald.template.jinja import JinjaTemplateEngine


class TemplateConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    directory: Union[DirectoryPath, List[DirectoryPath]]
    engine: Type[TemplateEngineProtocol] = JinjaTemplateEngine
