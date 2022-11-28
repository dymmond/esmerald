from typing import TYPE_CHECKING, List, Union

from esmerald.exceptions import MissingDependency, TemplateNotFound
from esmerald.protocols.template import TemplateEngineProtocol

if TYPE_CHECKING:
    from pydantic import DirectoryPath

try:
    from mako.exceptions import TemplateLookupException as MakoTemplateNotFound
    from mako.lookup import TemplateLookup
    from mako.template import Template as MakoTemplate
except ImportError as exc:
    raise MissingDependency("mako is not installed") from exc


class MakoTemplateEngine(TemplateEngineProtocol[MakoTemplate]):
    def __init__(self, directory: Union["DirectoryPath", List["DirectoryPath"]]) -> None:
        super().__init__(directory)
        self.engine = TemplateLookup(
            directories=directory if isinstance(directory, (list, tuple)) else [directory]
        )

    def get_template(self, template_name: str) -> MakoTemplate:
        try:
            return self.engine.get_template(template_name)
        except MakoTemplateNotFound as e:
            raise TemplateNotFound(template_name=template_name) from e
