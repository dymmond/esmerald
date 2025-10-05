from typing import Optional

from ravyn import Ravyn, Extension
from ravyn.types import DictAny


class MyExtension(Extension):
    def __init__(self, app: Optional["Ravyn"] = None, **kwargs: "DictAny"):
        super().__init__(app, **kwargs)
        self.app = app
        self.kwargs = kwargs

    def extend(self, **kwargs: "DictAny") -> None:
        """
        Function that should always be implemented when extending
        the Extension class or a `NotImplementedError` is raised.
        """
        # Do something here
