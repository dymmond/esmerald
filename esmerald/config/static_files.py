from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, DirectoryPath, constr, validator
from starlette.staticfiles import StaticFiles

from esmerald.utils.url import clean_path

if TYPE_CHECKING:
    from starlette.types import ASGIApp


class StaticFilesConfig(BaseModel):
    path: constr(min_length=1)  # type: ignore
    directory: Optional[DirectoryPath] = None
    html: bool = False
    packages: Optional[List[Union[str, Tuple[str, str]]]] = None
    check_dir: bool = True

    @validator("path")
    def validate_path(cls, value: str) -> str:  # pylint: disable=no-self-argument
        if "{" in value:
            raise ValueError("path parameters are not supported for static files")
        return clean_path(value)

    def _build_kwargs(
        self,
    ) -> Dict[str, Union[bool, int, DirectoryPath, List[Union[str, Tuple[str, str]]]]]:
        """
        Builds the necessary kwargs to create an StaticFiles object.
        """
        kwargs = {"html": self.html, "check_dir": self.check_dir}
        if self.packages:
            kwargs.update({"packages": self.packages})
        if self.directory:
            kwargs.update({"directory": str(self.directory)})
        return kwargs

    def to_app(self) -> "ASGIApp":
        """
        It can be three scenarios
        """

        return StaticFiles(**self._build_kwargs())
