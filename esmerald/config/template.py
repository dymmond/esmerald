from typing import List, Type, Union

from pydantic import BaseConfig, BaseModel, DirectoryPath

from esmerald.template.base import TemplateEngineProtocol
from esmerald.template.jinja import JinjaTemplateEngine


class TemplateConfig(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    directory: Union[DirectoryPath, List[DirectoryPath]]
    engine: Type[TemplateEngineProtocol] = JinjaTemplateEngine
