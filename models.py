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
class RonObject:
    v: RonValue

    def expect_map(self) -> RonMap:
        if isinstance(self, RonMap):
            return self
        raise ValueError(f"Value '{self}' is not a map")

    def expect_struct(self) -> RonStruct:
        if isinstance(self, RonStruct):
            return self
        raise ValueError(f"Value '{self}' is not a struct")

    def __getitem__(self, item: str | int) -> "RonObject":
        val = self.v
        container = val

        if isinstance(val, RonStruct):
            container = val._fields  # type: ignore
        elif isinstance(val, RonMap):
            container = val.entries  # type: ignore
        elif isinstance(val, RonTuple):
            container = val.elements

        result: RonValue

        if isinstance(container, dict):
            result = container[item]  # type: ignore
        elif isinstance(container, list):
            if not isinstance(item, int):
                raise TypeError(
                    f"List indices must be integers, got {type(item).__name__}"
                )
            result = container[item]
        else:
            raise TypeError(
                f"Value of type {type(val).__name__} is not subscriptable"
            )

        return RonObject(result)


@dataclass(frozen=True)
class RonStruct:
    name: str
    _fields: dict[str, RonValue] | list[RonValue]

    @property
    def as_dict(self) -> dict[str, RonValue]:
        """Return dict or die"""
        if isinstance(self._fields, dict):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Tuple-Struct, not a Named-Struct"
        )

    @property
    def as_list(self) -> list[RonValue]:
        """Return tuple or die"""
        if isinstance(self._fields, list):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Named-Struct, not a Tuple-Struct"
        )


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
