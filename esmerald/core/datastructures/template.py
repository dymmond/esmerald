from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.base import ResponseContainer  # noqa
from esmerald.exceptions import TemplateNotFound  # noqa
from esmerald.responses import TemplateResponse  # noqa
from esmerald.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Template(ResponseContainer[TemplateResponse]):
    """
    Template allows to pass the original template name and an alternative in case of exception
    not found.
    """

    name: Annotated[
        str,
        Doc(
            """
            The template name in the format of a *path*.

            Example: `templates/base/index.html`
            """
        ),
    ]
    context: Annotated[
        Optional[Dict[str, Any]],
        Doc(
            """
            Any context that should be sent to the templates to be rendered.

            **Example**

            ```python
            from esmerald import Esmerald, Gateway, Template, get
            from esmerald.datastructures import Cookie, ResponseHeader


            @get(
                path="/home",
                response_headers={"local-header": ResponseHeader(value="my-header")},
                response_cookies=[
                    Cookie(key="redirect-cookie", value="redirect-cookie"),
                    Cookie(key="general-cookie", value="general-cookie"),
                ],
            )
            def home() -> Template:
                return Template(
                    name="my-tem",
                    context={"user": "me"},
                    alternative_template=...,
                )

            ```
            """
        ),
    ] = {}
    alternative_template: Annotated[
        Optional[str],
        Doc(
            """
            An alternative template name if the `name` is not found.
            This should also be in the format of a *path*.

            Example: `templates/base/alternative_index.html`
            """
        ),
    ] = None

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> "TemplateResponse":
        from esmerald.exceptions import ImproperlyConfigured
        from esmerald.responses import TemplateResponse

        if not app.template_engine:
            raise ImproperlyConfigured("Template engine is not configured")

        data: Dict[str, Any] = {
            "background": self.background,
            "context": self.context,
            "headers": headers,
            "status_code": status_code,
            "template_engine": app.template_engine,
            "media_type": media_type,
        }
        try:
            return TemplateResponse(template_name=self.name, **data)
        except TemplateNotFound as e:  # pragma: no cover
            if self.alternative_template:
                try:
                    return TemplateResponse(template_name=self.alternative_template, **data)
                except TemplateNotFound as ex:  # pragma: no cover
                    raise ex
            raise e
