from typing import TYPE_CHECKING, Any, Dict, List, Union

from esmerald.exceptions import MissingDependency, TemplateNotFound
from esmerald.protocols.template import TemplateEngineProtocol

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import DirectoryPath

try:
    from mako.exceptions import TemplateLookupException as MakoTemplateNotFound
    from mako.lookup import TemplateLookup
    from mako.template import Template as MakoTemplate
except ImportError as exc:  # pragma: no cover
    raise MissingDependency("mako is not installed") from exc


class MakoTemplateEngine(TemplateEngineProtocol[MakoTemplate]):
    def __init__(
        self,
        directory: Union["DirectoryPath", List["DirectoryPath"]],
        env: Union[Any, None] = None,
        **env_options: Dict[Any, Any],
    ) -> None:
        super().__init__(directory)
        self.engine = TemplateLookup(
            directories=directory if isinstance(directory, (list, tuple)) else [directory]
        )
        self.options = env_options
        self.env = env

    def get_template(self, template_name: str) -> MakoTemplate:  # pragma: no cover
        try:
            return self.engine.get_template(template_name)
        except MakoTemplateNotFound as e:
            raise TemplateNotFound(name=template_name) from e
