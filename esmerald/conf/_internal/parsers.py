import json
import os
from typing import (
    Annotated,
    Any,
    Union,
    get_args,
    get_origin,
)

from esmerald.conf._internal.exceptions import SettingsError

_FALSE = {"0", "off", "f", "false", "n", "no"}
_TRUE = {"1", "on", "t", "true", "y", "yes"}


def _parse_bool(string: str) -> bool:
    """
    Parse a string as a boolean value.

    Args:
        s (str): The string to parse.

    Returns:
        bool: The parsed boolean value.

    Raises:
        SettingsError: If the string cannot be parsed as a boolean.
    """
    value = string.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise SettingsError(f"Invalid boolean: {string!r}")


def _simple_env_parse_line(line: str) -> tuple[str, str] | None:
    """
    A very simple parser for .env lines.

    Args:
        line (str): A line from a .env file.

    Returns:
        Optional[Tuple[str, str]]: A tuple of (key, value) if the line is valid, None otherwise.
    """
    # Minimal .env parser: KEY=VALUE, supports quoted values, ignores comments and blanks.
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # split on first '='
    if "=" not in line:
        return None

    # split on first '='
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip()

    # strip optional quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1]
    return key, value


def _load_dotenv(path: str) -> dict[str, str]:
    """
    Load a .env file and return a dictionary of environment variables.

    Args:
        path (str): The path to the .env file.

    Returns:
        dict[str, str]: A dictionary of environment variables.
    """
    env: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                kv = _simple_env_parse_line(raw)
                if kv:
                    key, value = kv
                    env[key] = value
    except FileNotFoundError:
        ...
    return env


def _load_secrets_dir(path: str) -> dict[str, str]:
    """
    Load a directory of secret files and return a dictionary of secrets.

    Args:
        path (str): The path to the directory containing secret files.

    Returns:
        dict[str, str]: A dictionary of secrets, where the key is the filename and the value is the file content.
    """
    # Load files as variables; filename -> content
    out: dict[str, str] = {}
    if not path:
        return out
    try:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if os.path.isfile(full):
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        out[name] = f.read().strip()
                except Exception:
                    # ignore unreadable file
                    continue
    except Exception:
        ...
    return out


def _strip_annotated(typ: Any) -> Any:
    """
    Strip Annotated from a type, if present.

    Args:
        typ (Any): The type to strip.

    Returns:
        Any: The stripped type.
    """
    origin = get_origin(typ)
    if origin is Annotated:
        return get_args(typ)[0]
    return typ


def _is_optional(typ: Any) -> bool:
    """
    Check if a type is Optional (i.e., Union with None).

    Args:
        typ (Any): The type to check.

    Returns:
        bool: True if the type is Optional, False otherwise.
    """
    typ = _strip_annotated(typ)
    origin = get_origin(typ)
    if origin is Union:
        return type(None) in get_args(typ)

    # Python 3.10 `| None` also yields origin=types.UnionType, but get_origin works
    try:
        import types

        if origin is types.UnionType:  # e.g., str | None
            return type(None) in get_args(typ)
    except Exception:
        ...
    return False


def _coerce(value: str, typ: Any) -> Any:
    """
    Coerce a string value to a target type.

    Args:
        value (str): The string value to coerce.
        typ (Any): The target type.

    Returns:
        Any: The coerced value.

    Raises:
        SettingsError: If the value cannot be coerced to the target type.

    Supported coercions:
    - scalar types (int, float, str, etc.): Cast str -> target type.
    - Optional/Union[NonNone] : resolve to the single non-None type if unambiguous.
    - bool: Pydantic-like boolean string set.
    - list/set/dict/tuple: parse JSON and (best-effort) coerce members.
    - nested BaseSettings: parse JSON or merge from nested env dict (caller handles).
    """
    typ = _strip_annotated(typ)
    origin = get_origin(typ)

    # Resolve Optional[T]
    if origin in (Union, getattr(__import__("types"), "UnionType", Union)):  # support 3.10 '|'
        args = [arg for arg in get_args(typ) if arg is not type(None)]
        if len(args) == 1:
            typ = args[0]
            origin = get_origin(typ)
        else:
            raise SettingsError(f"Ambiguous Union type: {typ!r}")

    # bool
    if typ is bool or str(typ) == "bool":
        return _parse_bool(value)

    # scalar coercion fast-path
    if origin is None:
        try:
            return typ(value)
        except Exception:
            # try JSON in case typ is str-like but value is quoted JSON representing same
            try:
                loaded = json.loads(value)
                if isinstance(loaded, (str, int, float, bool)):
                    return loaded
            except Exception:
                ...
            raise SettingsError(
                f"Cannot cast {value!r} to {getattr(typ, '__name__', str(typ))}"
            ) from None

    # collections via JSON
    try:
        loaded = json.loads(value)
    except Exception:
        raise SettingsError(f"Expected JSON for {typ}, got {value!r}") from None

    if origin in (list, set, tuple):
        (element_type,) = get_args(typ) or (Any,)

        def cast_elem(element: Any) -> Any:
            if isinstance(element, str):
                try:
                    return _coerce(element, element_type)
                except SettingsError:
                    ...

            # best-effort: if already of correct type or simple scalar, return as is
            return element if element_type in (Any, object) else element

        sequence = [cast_elem(x) for x in loaded]
        if origin is list:
            return sequence
        if origin is set:
            return set(sequence)
        if origin is tuple:
            return tuple(sequence)

    if origin is dict:
        key_type, value_type = get_args(typ) or (Any, Any)
        parsed_dict: dict[Any, Any] = {}

        for raw_key, raw_value in loaded.items():
            # Keys: currently assume str; could add conversion if key_type != str
            coerced_key = raw_key if key_type in (Any, object) else raw_key

            # Values: try to coerce if it's a string, otherwise keep as-is
            if isinstance(raw_value, str):
                try:
                    coerced_value = _coerce(raw_value, value_type)
                except SettingsError:
                    coerced_value = raw_value  # fallback if coercion fails
            else:
                coerced_value = raw_value

            parsed_dict[coerced_key] = coerced_value

        return parsed_dict

    # Fallback: return JSON-decoded value
    return loaded
