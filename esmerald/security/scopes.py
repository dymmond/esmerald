from typing import List, Union

from typing_extensions import Annotated, Doc


class Scopes:
    """
    This class is used in a dependency parameter to get the OAuth2 scopes required by all dependencies in the chain.

    It allows multiple dependencies to have different scopes, even when used in the same path operation.
    With this class, you can access all the required scopes from all dependencies in one place.

    For more details, refer to the
    [Esmerald documentation on OAuth2 scopes](https://esmerald.dev/security/advanced/oauth2-scopes/).
    """

    def __init__(
        self,
        scopes: Annotated[
            Union[List[str], None],
            Doc(
                """
                This will be filled by Esmerald.
                """
            ),
        ] = None,
    ):
        self.scopes: Annotated[
            List[str],
            Doc(
                """
                The list of all the scopes required by dependencies.
                """
            ),
        ] = (
            scopes or []
        )
        self.scope_str: Annotated[
            str,
            Doc(
                """
                All the scopes required by all the dependencies in a single string
                separated by spaces, as defined in the OAuth2 specification.
                """
            ),
        ] = " ".join(self.scopes)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(scopes={self.scopes})"
