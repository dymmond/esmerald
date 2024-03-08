from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Union

from esmerald.exceptions import MissingDependency, TemplateNotFound
from esmerald.protocols.template import TemplateEngineProtocol

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import DirectoryPath

try:
    from jinja2 import (
        Environment,
        FileSystemLoader,
        Template as JinjaTemplate,
        TemplateNotFound as JinjaTemplateNotFound,
    )
except ImportError as exc:  # pragma: no cover
    raise MissingDependency("jinja2 is not installed") from exc


try:
    import jinja2

    if hasattr(jinja2, "pass_context"):
        pass_context = jinja2.pass_context
    else:  # pragma: nocover
        pass_context = jinja2.contextfunction  # type: ignore[attr-defined]
except ImportError:  # pragma: nocover
    jinja2 = None


class JinjaTemplateEngine(TemplateEngineProtocol[JinjaTemplate]):  # type: ignore
    def __init__(
        self, directory: Union["DirectoryPath", List["DirectoryPath"]], **env_options: Any
    ) -> None:
        super().__init__(directory)
        self.env = self._create_environment(directory, **env_options)

    def _create_environment(
        self, directory: Union[str, PathLike, List[Path]], **env_options: Any
    ) -> "Environment":
        @pass_context
        def url_for(context: dict, name: str, **path_params: Any) -> Any:
            request = context["request"]
            return request.path_for(name, **path_params)

        loader = FileSystemLoader(directory)
        env_options.setdefault("loader", loader)

        env = Environment(autoescape=True, **env_options)
        env.globals["url_for"] = url_for
        return env

    def get_template(self, template_name: str) -> JinjaTemplate:
        try:
            return self.env.get_template(template_name)
        except JinjaTemplateNotFound as e:  # pragma: no cover
            raise TemplateNotFound(template_name=template_name) from e
