from __future__ import annotations

from dataclasses import dataclass

type RonValue = (
    RonStruct
    | RonTuple
    | RonMap
    | RonOptional
    | RonChar
    | int
    | float
    | str
    | bool
    | list["RonValue"]
)


@dataclass
class RonStruct:
    name: str
    fields: dict[str, RonValue] | list[RonValue]


@dataclass
class RonTuple:
    elements: list[RonValue]


@dataclass
class RonMap:
    entries: dict[RonValue, RonValue]


@dataclass
class RonOptional:
    value: RonValue | None


@dataclass
class RonChar:
    value: str
