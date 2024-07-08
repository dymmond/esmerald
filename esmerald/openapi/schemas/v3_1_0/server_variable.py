from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ServerVariable(BaseModel):
    """An object representing a Server Variable for server URL template
    substitution."""

    enum: Optional[List[str]] = None
    """
    An enumeration of string values to be used if the substitution options are from a limited set.
    The array SHOULD NOT be empty.
    """

    default: str
    """
    **REQUIRED**. The default value to use for substitution,
    which SHALL be sent if an alternate value is _not_ supplied.
    Note this behavior is different than the [Schema Object's](https://spec.openapis.org/oas/v3.1.0#schemaObject) treatment of default values,
    because in those cases parameter values are optional.
    If the [enum](https://spec.openapis.org/oas/v3.1.0#serverVariableEnum) is defined, the value MUST exist in the enum's values.
    """

    description: Optional[str] = None
    """
    An optional description for the server variable.
    [CommonMark syntax](https://spec.commonmark.org/) MAY be used for rich text representation.
    """
    model_config = ConfigDict(extra="ignore")
