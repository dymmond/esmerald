import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, cast

from pydantic import FilePath, validator  # noqa
from starlette.responses import FileResponse  # noqa

from esmerald.datastructures.base import ResponseContainer

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType


class File(ResponseContainer[FileResponse]):
    path: FilePath
    filename: str
    stat_result: Optional[os.stat_result] = None

    @validator("stat_result", always=True)
    def validate_status_code(  # pylint: disable=no-self-argument
        cls, value: Optional[os.stat_result], values: Dict[str, Any]
    ) -> os.stat_result:
        """Set the stat_result value for the given filepath."""
        return value or os.stat(cast("str", values.get("path")))

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
