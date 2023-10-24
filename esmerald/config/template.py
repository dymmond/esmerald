from typing import List, Type, Union

from pydantic import BaseModel, ConfigDict, DirectoryPath
from typing_extensions import Annotated, Doc

from esmerald.protocols.template import TemplateEngineProtocol
from esmerald.template.jinja import JinjaTemplateEngine


class TemplateConfig(BaseModel):
    """
    An instance of [TemplateConfig](https://esmerald.dev/configurations/template/).

    This configuration is a simple set of configurations that when passed enables the template engine.

    !!! Note
        You might need to install the template engine before
        using this. You can always run
        `pip install esmerald[templates]` to help you out.

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
