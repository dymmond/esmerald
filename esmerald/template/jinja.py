from os import PathLike
from typing import TYPE_CHECKING, Any, List, Union

from esmerald.exceptions import MissingDependency, TemplateNotFound
from esmerald.protocols.template import TemplateEngineProtocol

if TYPE_CHECKING:
    from pydantic import DirectoryPath

try:
    from jinja2 import Environment, FileSystemLoader
    from jinja2 import Template as JinjaTemplate
    from jinja2 import TemplateNotFound as JinjaTemplateNotFound
except ImportError as exc:
    raise MissingDependency("jinja2 is not installed") from exc


try:
    import jinja2

    # @contextfunction was renamed to @pass_context in Jinja 3.0, and was removed in 3.1
    # hence we try to get pass_context (most installs will be >=3.1)
    # and fall back to contextfunction,
    # adding a type ignore for mypy to let us access an attribute that may not exist
    if hasattr(jinja2, "pass_context"):
        pass_context = jinja2.pass_context
    else:  # pragma: nocover
        pass_context = jinja2.contextfunction  # type: ignore[attr-defined]
except ImportError:  # pragma: nocover
    jinja2 = None  # type: ignore


class JinjaTemplateEngine(TemplateEngineProtocol[JinjaTemplate]):
    def __init__(
        self, directory: Union["DirectoryPath", List["DirectoryPath"]], **env_options: Any
    ) -> None:
        super().__init__(directory)
        self.env = self._create_environment(directory, **env_options)

    def _create_environment(
        self, directory: Union[str, PathLike], **env_options: Any
    ) -> "jinja2.Environment":
        @pass_context
        def url_for(context: dict, name: str, **path_params: Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        loader = FileSystemLoader(directory)
        env_options.setdefault("loader", loader)
        env_options.setdefault("autoescape", True)

        env = Environment(**env_options)
        env.globals["url_for"] = url_for
        return env

    def get_template(self, name: str) -> JinjaTemplate:
        return self.env.get_template(name)

    def _get_template(self, template_name: str) -> JinjaTemplate:
        try:
            return self.engine.get_template(name=template_name)
        except JinjaTemplateNotFound as e:
            raise TemplateNotFound(template_name=template_name) from e
