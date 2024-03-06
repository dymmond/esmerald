from mimetypes import guess_type
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from lilya.types import Receive, Scope, Send

from esmerald.enums import MediaType
from esmerald.responses.base import Response

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.backgound import BackgroundTask, BackgroundTasks
    from esmerald.protocols.template import TemplateEngineProtocol
    from esmerald.types import ResponseCookies


class TemplateResponse(Response):
    def __init__(
        self,
        template_name: str,
        template_engine: "TemplateEngineProtocol",
        status_code: int = 200,
        context: Optional[Dict[str, Any]] = None,
        background: Optional[Union["BackgroundTask", "BackgroundTasks"]] = None,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional["ResponseCookies"] = None,
        media_type: Union[MediaType, str] = MediaType.HTML,
    ):
        if media_type == MediaType.JSON:  # we assume this is the default
            suffixes = PurePath(template_name).suffixes
            for suffix in suffixes:
                _type = guess_type("name" + suffix)[0]
                if _type:
                    media_type = _type
                    break
            else:
                media_type = MediaType.TEXT  # pragma: no cover

        self.template = template_engine.get_template(template_name)
        self.context = context or {}
        content = self.template.render(**context)
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
            cookies=cookies,
        )

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:  # pragma: no cover
        request = self.context.get("request", {})
        extensions = request.get("extensions", {})
        if "http.response.template" in extensions:
            await send(
                {
                    "type": "http.response.template",
                    "template": self.template,
                    "context": self.context,
                }
            )
        await super().__call__(scope, receive, send)
