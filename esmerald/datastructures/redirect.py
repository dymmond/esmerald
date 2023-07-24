from typing import TYPE_CHECKING, Any, Dict, Type, Union

from starlette.responses import RedirectResponse  # noqa

from esmerald.datastructures.base import ResponseContainer  # noqa
from esmerald.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Redirect(ResponseContainer[RedirectResponse]):
    path: str

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> RedirectResponse:
        return RedirectResponse(
            headers=headers,
            status_code=status_code,
            url=self.path,
            background=self.background,
        )
