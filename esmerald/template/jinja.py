from typing import TYPE_CHECKING, Any, List, Union

from lilya.templating.jinja import Jinja2Template

from esmerald.exceptions import MissingDependency

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import DirectoryPath

try:
    from jinja2 import Environment
except ImportError as exc:  # pragma: no cover
    raise MissingDependency("jinja2 is not installed") from exc


class JinjaTemplateEngine(Jinja2Template):
    def __init__(
        self,
        directory: Union["DirectoryPath", List["DirectoryPath"]],
        env: Union[Environment, None] = None,
        **env_options: Any,
    ) -> None:
        super().__init__(directory=directory, env=env, **env_options)

    def get_template_render_function(self) -> str:
        return "render_async" if self.env.is_async else "render"
