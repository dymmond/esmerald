import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, cast

from lilya.responses import FileResponse  # noqa
from pydantic import FilePath, model_validator  # noqa
from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.base import ResponseContainer
from esmerald.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class File(ResponseContainer[FileResponse]):
    path: Annotated[
        FilePath,
        Doc(
            """
            The path to the file to download.
            """
        ),
    ]
    filename: Annotated[
        str,
        Doc(
            """
            The name of the file to be added to the `Content-Disposition` attachment.
            """
        ),
    ]
    stat_result: Annotated[
        Optional[os.stat_result],
        Doc(
            """
            The equivalent of the `os.stat_result`.
            """
        ),
    ] = None

    @model_validator(mode="before")
    def validate_fields(cls, values: Dict[str, Any]) -> Any:
        stat_result = values.get("stat_result")
        values["stat_result"] = stat_result or os.stat(cast("str", values.get("path")))
        return values

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> FileResponse:
        return FileResponse(
            background=self.background,
            filename=self.filename,
            headers=headers,
            media_type=media_type,
            path=self.path,
            stat_result=self.stat_result,
            status_code=status_code,
        )
