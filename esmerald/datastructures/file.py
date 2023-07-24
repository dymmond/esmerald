import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, cast

from pydantic import FilePath, field_validator, model_validator  # noqa
from starlette.responses import FileResponse  # noqa

from esmerald.datastructures.base import ResponseContainer
from esmerald.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class File(ResponseContainer[FileResponse]):
    path: FilePath
    filename: str
    stat_result: Optional[os.stat_result] = None

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
