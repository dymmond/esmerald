from typing import List, Type, Union

from esmerald.protocols.template import TemplateEngineProtocol
from esmerald.template.jinja import JinjaTemplateEngine
from pydantic import BaseConfig, BaseModel, DirectoryPath


class TemplateConfig(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    directory: Union[DirectoryPath, List[DirectoryPath]]
    engine: Type[TemplateEngineProtocol] = JinjaTemplateEngine
