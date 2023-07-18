from typing import Any

from starlette.datastructures import ImmutableMultiDict

from esmerald.datastructures import UploadFile


class FormMultiDict(ImmutableMultiDict[str, Any]):
    async def close(self) -> None:
        for _, value in self.multi_items():
            if isinstance(value, UploadFile):
                await value.close()
