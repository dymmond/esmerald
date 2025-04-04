from typing import Any, Dict, List, Type, Union

from pydantic import BaseModel, ConfigDict, DirectoryPath
from typing_extensions import Annotated, Doc

from esmerald.protocols.template import TemplateEngineProtocol
from esmerald.template.jinja import JinjaTemplateEngine


class TemplateConfig(BaseModel):
    """
    An instance of [TemplateConfig](https://esmerald.dev/configurations/template/).

    This configuration is a simple set of configurations that when passed enables the template engine.

    **Example**

    ```python
    from esmerald import Esmerald
    from esmerald.config.template import TemplateConfig
    from esmerald.template.jinja import JinjaTemplateEngine

    template_config = TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    )

    app = Esmerald(template_config=template_config)
    ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    engine: Annotated[
        Type[TemplateEngineProtocol],
        Doc(
            """
            The template engine to be used.
            """
        ),
    ] = JinjaTemplateEngine

    directory: Annotated[
        Union[DirectoryPath, List[DirectoryPath]],
        Doc(
            """
            The directory for the templates in the format of a path like.

            Example: `/templates`.
            """
        ),
    ]
    env: Annotated[
        Union[Any, None],
        Doc(
            """
            The environment for the template engine.
            This env is **only used for jinja2** templates and its ignored for other template engines.

            The `env` is a `jinja2.Environment` instance.
            """
        ),
    ] = None
    env_options: Annotated[
        Union[Dict[Any, Any], None],
        Doc(
            """
            The options for the template engine. These options are passed to the template engine.

            In the case of the `jinja2` template engine, these options are passed to the `jinja2.Environment` instance and will populate the `env_options` parameter.

            This is currently only used for the `jinja2` template engine and nothing else.
            """
        ),
    ] = {}
