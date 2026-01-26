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


@dataclass(frozen=True)
class RonStruct:
    name: str
    fields: dict[str, RonValue] | list[RonValue]


@dataclass(frozen=True)
class RonTuple:
    elements: list[RonValue]


@dataclass(frozen=True)
class RonMap:
    entries: dict[RonValue, RonValue]


@dataclass(frozen=True)
class RonOptional:
    value: RonValue | None


@dataclass(frozen=True)
class RonChar:
    value: str
