from typing import TYPE_CHECKING, Any, Dict, Type, Union

from lilya import status
from lilya.responses import RedirectResponse  # noqa
from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.base import ResponseContainer  # noqa
from esmerald.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Redirect(ResponseContainer[RedirectResponse]):
    path: Annotated[
        str,
        Doc(
            """
            The url path to redirect.
            This should be in format of `/<str>`.

            Example: `/redirect-page`.
            """
        ),
    ]
    status_code: Annotated[
        int,
        Doc(
            """
            The status code of the response.
            This should be in format of `int`.

            Example: `301`.
            """
        ),
    ] = status.HTTP_307_TEMPORARY_REDIRECT

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
