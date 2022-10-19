import re
from typing import Iterable


def clean_path(path: str) -> str:
    """Make sure a given path by ensuring it starts with a slash and does not
    end with a slash.
    """
    path = path.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub("//+", "/", path)
    return path


def join_paths(paths: Iterable[str]) -> str:
    return clean_path("/".join(paths))
