import inspect
import json
import os
from functools import cached_property
from typing import (
    Any,
    get_args,
    get_origin,
)

from esmerald import __version__  # noqa
from esmerald.conf._internal.config import SettingsConfig
from esmerald.conf._internal.exceptions import SettingsError
from esmerald.conf._internal.parsers import (
    _coerce,
    _is_optional,
    _load_dotenv,
    _load_secrets_dir,
    _strip_annotated,
)


class BaseSettings:
    """
    Base class for settings management.

    This class provides functionality to load settings from environment variables,
    .env files, and secret directories, with support for type coercion and nested settings.

    Attributes:
        __config__ (SettingsConfig): Configuration for settings management.
        __type_hints__ (dict[str, Any] | None): Cached type hints for the settings fields.

    Usage:
        class App(BaseSettings):
            __config__ = SettingsConfig()
            __config__.env_prefix = "MYAPP_"
            __config__.env_file = ".env"
            __config__.secrets_dir = "/run/secrets"
            __config__.env_map = {"db_url": "DATABASE_URL"}

            debug: bool = False
            db_url: str
            workers: int = 4
            tags: list[str] = []

        settings = App()                 # loads from env/.env/secrets
        settings = App(db_url="...")     # kwargs override env
    """

    __config__ = SettingsConfig()
    __type_hints__: dict[str, Any] | None = None

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize settings by loading from environment variables, .env file, secrets directory,
        and any provided keyword arguments.

        Keyword Args:
            **kwargs: Settings values provided as keyword arguments, which take precedence
                      over environment variables, .env file, and secrets directory.
        Raises:
            SettingsError: If required settings are missing or if there are issues with type coercion.
        """
        cls = self.__class__
        if cls.__type_hints__ is None:
            cls.__type_hints__ = dict(getattr(cls, "__annotations__", {}))

        cfg = cls.__config__
        env_map = cfg.env_map or {}

        # load sources
        dotenv_map = _load_dotenv(cfg.env_file) if cfg.env_file else {}
        secrets_map = _load_secrets_dir(cfg.secrets_dir) if cfg.secrets_dir else {}

        # precedence: kwargs > env > dotenv > secrets > defaults
        for field, typ in cls.__type_hints__.items():
            base_type = _strip_annotated(typ)

            # 1) kwargs
            if field in kwargs:
                value = kwargs[field]
                setattr(self, field, value)
                continue

            # compute the env var name
            env_name = env_map.get(field)
            if not env_name:
                # apply prefix if present
                name = f"{cfg.env_prefix or ''}{field}"
                env_name = name if cfg.case_sensitive else name.upper()

            # environment
            env_val = os.getenv(env_name)
            if cfg.env_ignore_empty and env_val == "":
                env_val = None

            # .env file (if not in os.environ)
            if env_val is None:
                # .env names are case-sensitive by convention; also try upper if not case_sensitive
                env_val = dotenv_map.get(env_name)
                if env_val is None and not cfg.case_sensitive:
                    env_val = dotenv_map.get(env_name.upper())

            # secrets dir (lowest external priority)
            if env_val is None:
                env_val = secrets_map.get(env_name)
                if env_val is None and not cfg.case_sensitive:
                    env_val = secrets_map.get(env_name.upper())

            if env_val is not None:
                try:
                    value = self._coerce_with_nesting(field, env_val, base_type, cfg)
                except SettingsError as e:
                    raise SettingsError(f"Field {field!r}: {e}") from None
                setattr(self, field, value)
            else:
                # default from class attribute (may not exist)
                if hasattr(self, field):
                    setattr(self, field, getattr(self, field))
                else:
                    # leave as None; if required, we’ll validate later
                    setattr(self, field, None)

        # required check
        self._validate_required()

        # hook
        self.post_init()

    def post_init(self) -> None: ...

    def model_dump(
        self,
        exclude_none: bool = False,
        upper: bool = False,
        exclude: set[str] | None = None,
        include_properties: bool = False,
    ) -> dict[str, Any]:
        """
        Dump the model's data as a dictionary.

        Args:
            exclude_none (bool): Whether to exclude fields with None values.
            upper (bool): Whether to convert field names to uppercase.
            exclude (set[str] | None): A set of field names to exclude from the output.
            include_properties (bool): Whether to include properties in the output.
        Returns:
            dict[str, Any]: The model's data as a dictionary.
        """
        return self.dict(
            exclude_none=exclude_none,
            upper=upper,
            exclude=exclude,
            include_properties=include_properties,
        )

    def model_dump_json(
        self,
        exclude_none: bool = False,
        upper: bool = False,
        exclude: set[str] | None = None,
        include_properties: bool = False,
        **json_kwargs: Any,
    ) -> str:
        """
        Dump the model's data as a JSON string.

        Args:
            exclude_none (bool): Whether to exclude fields with None values.
            upper (bool): Whether to convert field names to uppercase.
            exclude (set[str] | None): A set of field names to exclude from the output.
            include_properties (bool): Whether to include properties in the output.
            **json_kwargs: Additional keyword arguments to pass to json.dumps().
        Returns:
            str: The model's data as a JSON string.
        """
        return json.dumps(
            self.dict(
                exclude_none=exclude_none,
                upper=upper,
                exclude=exclude,
                include_properties=include_properties,
            ),
            **json_kwargs,
        )

    def dict(
        self,
        exclude_none: bool = False,
        upper: bool = False,
        exclude: set[str] | None = None,
        include_properties: bool = False,
    ) -> dict[str, Any]:
        """
        Convert the settings instance to a dictionary.

        Args:
            exclude_none (bool): Whether to exclude fields with None values.
            upper (bool): Whether to convert field names to uppercase.
            exclude (set[str] | None): A set of field names to exclude from the output.
            include_properties (bool): Whether to include properties in the output.
        Returns:
            dict[str, Any]: The settings as a dictionary.
        """
        result: dict[str, Any] = {}
        exclude = exclude or set()

        for key in self.__annotations__:
            if key in exclude:
                continue
            val = getattr(self, key, None)
            if exclude_none and val is None:
                continue
            result[key.upper() if upper else key] = val

        if include_properties:
            for name, _ in inspect.getmembers(
                type(self), lambda o: isinstance(o, (property, cached_property))
            ):
                if name in exclude or name in self.__annotations__:
                    continue
                try:
                    val = getattr(self, name)
                    if exclude_none and val is None:
                        continue
                    result[name.upper() if upper else name] = val
                except Exception:
                    continue

        return result

    def tuple(
        self,
        exclude_none: bool = False,
        upper: bool = False,
        exclude: set[str] | None = None,
        include_properties: bool = False,
    ) -> list[tuple[str, Any]]:
        """
        Convert the settings instance to a list of key-value pairs (tuples).

        Args:
            exclude_none (bool): Whether to exclude fields with None values.
            upper (bool): Whether to convert field names to uppercase.
            exclude (set[str] | None): A set of field names to exclude from the output.
            include_properties (bool): Whether to include properties in the output.
        Returns:
            list[tuple[str, Any]]: The settings as a list of key-value pairs.
        """
        return list(self.dict(exclude_none, upper, exclude, include_properties).items())

    def _validate_required(self) -> None:
        """
        Validate that all required settings are provided.

        Raises:
            SettingsError: If any required settings are missing.
        """
        errors = []
        for k, t in self.__type_hints__.items():
            v = getattr(self, k, None)
            if v is None and not _is_optional(t):
                errors.append(f"{k} (expected {t})")
        if errors:
            raise SettingsError("Missing required settings: " + ", ".join(errors))

    def _env_key_for_nested(self, cfg: SettingsConfig, names: list[str]) -> str:
        """
        Given a list of names representing a path in a nested settings structure,
        construct the corresponding environment variable key based on the provided configuration.

        Args:
            cfg (SettingsConfig): The settings configuration containing prefix, delimiter, and case sensitivity.
            names (list[str]): A list of strings representing the path in the nested structure.

        Returns:
            str: The constructed environment variable key.
        """
        # Build env key path with prefix + delimiter
        delimiter = cfg.env_nested_delimiter or "__"
        base = "".join([cfg.env_prefix or ""])
        key = delimiter.join(names)
        key_full = base + key
        return key_full if cfg.case_sensitive else key_full.upper()

    def _collect_nested_env_overrides(self, field: str, cfg: SettingsConfig) -> Any:
        """
        Scan environment for keys like PREFIX_field__sub__leaf and return
        a flat dict of "sub__leaf" -> value (and same for .env & secrets if desired).
        For simplicity we only read `os.environ` here; .env/secrets contribute via top-level JSON.
        """
        out: dict[str, str] = {}
        delim = cfg.env_nested_delimiter or "__"
        # search case-insensitive if cfg.case_sensitive=False
        prefix = f"{cfg.env_prefix or ''}{field}{delim}"
        candidates = os.environ.items()

        if not cfg.case_sensitive:
            prefix = prefix.upper()
            # normalize items to upper keys
            candidates = ((k.upper(), v) for k, v in os.environ.items())  # type: ignore

        for k, v in candidates:
            if k.startswith(prefix):
                suffix = k[len(prefix) :]  # e.g., "host" or "db__port"
                out[suffix] = v
        return out

    def _coerce_with_nesting(self, field: str, value: str, typ: Any, cfg: SettingsConfig) -> Any:
        """
        - If target type is another BaseSettings subclass, try:
            1) JSON decode `value` to dict and instantiate nested class
            2) Merge env Nested overrides using env_nested_delimiter.
        - For dict/list/set/tuple: JSON as in _coerce
        - For simple types: _coerce
        """
        typ = _strip_annotated(typ)
        origin = get_origin(typ)

        # nested settings model
        if inspect.isclass(typ) and issubclass(typ, BaseSettings):
            base_dict = {}
            # try JSON for base object
            try:
                decoded = json.loads(value)
                if isinstance(decoded, dict):
                    base_dict.update(decoded)
            except Exception:
                # allow simple string if nested has a single field named "value"
                base_dict = {}

            # collect nested overrides from env
            if cfg.env_nested_delimiter:
                nested_overrides = self._collect_nested_env_overrides(field, cfg)
                # flatten "A__B__C" keys into dict
                for path, raw in nested_overrides.items():
                    parts = path.split(cfg.env_nested_delimiter)
                    cursor = base_dict
                    for p in parts[:-1]:
                        cursor = cursor.setdefault(p, {})
                    cursor[parts[-1]] = raw

            # finally instantiate nested settings
            return typ(**base_dict)

        if origin is dict:
            _, val_t = get_args(typ) or (Any, Any)
            base_dict = {}
            # JSON base (if provided as a single env var with JSON)
            try:
                decoded = json.loads(value)
                if isinstance(decoded, dict):
                    base_dict.update(decoded)
            except Exception:
                # fall back to scalar coercion which will raise a helpful error if needed
                return _coerce(value, typ)

            # merge nested overrides FIELD__A__B=...
            if cfg.env_nested_delimiter:
                nested_overrides = self._collect_nested_env_overrides(field, cfg)
                for path, raw in nested_overrides.items():
                    parts = path.split(cfg.env_nested_delimiter)
                    cursor = base_dict
                    for p in parts[:-1]:
                        cursor = cursor.setdefault(p, {})
                    cursor[parts[-1]] = raw

            # (optional) best-effort value casting for leaf strings
            def cast_leaf(leaf: Any, t: Any) -> Any:
                if isinstance(leaf, str):
                    try:
                        return _coerce(leaf, t)
                    except Exception:
                        return leaf
                return leaf

            # walk once and coerce leaf values to val_t (keys keep str)
            stack = [base_dict]
            while stack:
                cur = stack.pop()
                for k, v in list(cur.items()):
                    if isinstance(v, dict):
                        stack.append(v)
                    else:
                        cur[k] = cast_leaf(v, val_t)
            return base_dict

        # collections & simple types
        return _coerce(value, typ)
