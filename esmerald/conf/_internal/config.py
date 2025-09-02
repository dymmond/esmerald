class SettingsConfig:
    """
    Configuration for settings management.

    Attributes:
        env_prefix (str | None): Prefix to add to environment variables.
        case_sensitive (bool): Whether to treat environment variables as case-sensitive.
        env_nested_delimiter (str | None): Delimiter for nested environment variables.
        env_ignore_empty (bool): Whether to ignore empty environment variables.
        env_file (str | None): Path to the .env file.
        secrets_dir (str | None): Path to the directory containing secret files.
        env_map (dict[str, str] | None): Mapping of environment variable names to field names.
    """

    env_prefix: str | None = None
    """
    Prefix to add to environment variables.
    """
    case_sensitive: bool = False
    """
    Whether to treat environment variables as case-sensitive.
    """
    env_nested_delimiter: str | None = "__"
    """
    Delimiter for nested environment variables.
    """
    env_ignore_empty: bool = False
    """
    Whether to ignore empty environment variables.
    """
    env_file: str | None = None
    """
    Path to the .env file.
    """
    secrets_dir: str | None = None
    """
    Path to the directory containing secret files.
    """
    env_map: dict[str, str] | None = None
    """
    Mapping of environment variable names to field names.
    """
