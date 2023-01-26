from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from esmerald.datastructures.base import ResponseContainer  # noqa
from esmerald.exceptions import TemplateNotFound  # noqa
from esmerald.responses import TemplateResponse  # noqa

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType


class Template(ResponseContainer[TemplateResponse]):
    """
    Template allows to pass the original template name and an alternative in case of exception
    not found.

    Args:
        name: Template name
        context: The context to be passed to the template
        alternative_template: The alternative template to be rendered if the original doesn't exist.
    """

    name: str
    context: Optional[Dict[str, Any]] = {}
    alternative_template: Optional[str] = None

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

        data = {
            "background": self.background,
            "context": self.context,
            "headers": headers,
            "status_code": status_code,
            "template_engine": app.template_engine,
            "media_type": media_type,
        }
        try:
            return TemplateResponse(template_name=self.name, **data)
        except TemplateNotFound as e:
            if self.alternative_template:
                return TemplateResponse(template_name=self.alternative_template, **data)
            raise e
