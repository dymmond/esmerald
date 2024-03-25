from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from lilya._internal._path import clean_path
from lilya.staticfiles import StaticFiles
from lilya.types import ASGIApp
from pydantic import BaseModel, DirectoryPath, constr, field_validator
from typing_extensions import Annotated, Doc


class StaticFilesConfig(BaseModel):
    """
    An instance of [StaticFilesConfig](https://esmerald.dev/configurations/staticfiles/).

    This configuration is used to enable and serve static files via
    Esmerald application.

    **Example**

    ```python
    from esmerald import Esmerald
    from esmerald.config import StaticFilesConfig

    static_files_config = StaticFilesConfig(
        path="/static", directory=Path("static")
    )

    app = Esmerald(static_files_config=static_files_config)
    ```
    """

    path: Annotated[  # type: ignore
        constr(min_length=1),
        Doc(
            """
            The path for the statics.
            """
        ),
    ]
    directory: Annotated[
        Optional[Union[DirectoryPath, str, Path, Any]],
        Doc(
            """
            The directory for the statics in the format of a path like.

            Example: `/static`.
            """
        ),
    ] = None
    html: Annotated[
        bool,
        Doc(
            """
            Run in HTML mode. Automatically loads index.html for directories if such file exist.
            """
        ),
    ] = False
    packages: Annotated[
        Optional[List[Union[str, Tuple[str, str]]]],
        Doc(
            """
            A list of strings or list of tuples of strings of python packages.
            """
        ),
    ] = None
    check_dir: Annotated[
        bool,
        Doc(
            """
            Ensure that the directory exists upon instantiation.
            """
        ),
    ] = True

    @field_validator("path")
    def validate_path(cls, value: str) -> str:
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
            kwargs.update({"packages": self.packages})  # type: ignore
        if self.directory:
            kwargs.update({"directory": str(self.directory)})  # type: ignore
        return kwargs  # type: ignore

    def to_app(self) -> ASGIApp:
        """
        It can be three scenarios
        """

        return StaticFiles(**self._build_kwargs())  # type: ignore
