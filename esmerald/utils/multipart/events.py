from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class PreambleEvent:
    __slots__ = ("data",)

    data: bytes


@dataclass
class FieldEvent:
    __slots__ = (
        "name",
        "headers",
    )

    name: str
    headers: Dict[str, str]


@dataclass
class FileEvent:
    __slots__ = (
        "name",
        "headers",
        "filename",
    )

    name: str
    filename: str
    headers: Dict[str, str]


@dataclass
class DataEvent:
    __slots__ = (
        "data",
        "more_data",
    )

    data: bytes
    more_data: bool


@dataclass
class EpilogueEvent:
    __slots__ = ("data",)

    data: bytes


MultipartMessageEvent = Union[PreambleEvent, FileEvent, FieldEvent, DataEvent, EpilogueEvent]
