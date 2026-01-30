from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeGuard

from frozendict import frozendict

type RonValue = (
    RonStruct
    | RonSeq
    | RonMap
    | RonOptional
    | RonChar
    | int
    | float
    | str
    | bool
)


def is_ron_value(val: Any) -> TypeGuard[RonValue]:
    # simple top-level check
    if isinstance(
        val,
        (
            RonStruct,
            RonSeq,
            RonMap,
            RonOptional,
            RonChar,
            int,
            float,
            str,
            bool,
        ),
    ):
        return True

    # nested "trust me bro" check
    if isinstance(val, tuple):
        return len(val) == 0 or is_ron_value(val[0])

    return False


@dataclass
class RonObject:
    v: RonValue

    def expect_map(self) -> RonMap:
        if isinstance(self.v, RonMap):
            return self.v
        raise ValueError(f"Value '{self}' is not a map")

    def expect_struct(self) -> RonStruct:
        if isinstance(self.v, RonStruct):
            return self.v
        raise ValueError(f"Value '{self}' is not a struct")

    def expect_int(self) -> int:
        if isinstance(self.v, int):
            return self.v
        raise ValueError(f"Value '{self}' is not an integer")

    def expect_float(self) -> float:
        if isinstance(self.v, float):
            return self.v
        raise ValueError(f"Value '{self}' is not a float")

    def expect_str(self) -> str:
        if isinstance(self.v, str):
            return self.v
        raise ValueError(f"Value '{self}' is not a string")

    def expect_bool(self) -> bool:
        if isinstance(self.v, bool):
            return self.v
        raise ValueError(f"Value '{self}' is not a boolean")

    def expect_tuple(self) -> RonSeq:
        if isinstance(self.v, RonSeq) and self.v.kind == "tuple":
            return self.v
        raise ValueError(f"Value '{self}' is not a ron tuple")

    def expect_list(self) -> RonSeq:
        if isinstance(self.v, RonSeq) and self.v.kind == "list":
            return self.v
        raise ValueError(f"Value '{self}' is not a ron list")

    def maybe(self) -> "RonObject" | None:
        """
        Converts Obj(Optional(v)) to Optional(Obj(v))
        """
        if isinstance(self.v, RonOptional):
            return RonObject(self.v.value) if self.v.value is not None else None
        raise ValueError(f"Value '{self}' is not an option")

    def __getitem__(self, item: RonValue) -> "RonObject":
        val = self.v

        if isinstance(val, RonStruct):
            container = val._fields
        elif isinstance(val, RonMap):
            container = val.entries
        elif isinstance(val, RonSeq):
            container = val.elements
        elif isinstance(val, tuple):
            container = val
        else:
            raise TypeError(f"{self}[{item}]")

        if isinstance(container, frozendict):
            result = container[item]
            return RonObject(result)
        elif isinstance(container, tuple):
            if not isinstance(item, int):
                raise TypeError(
                    f"List indices must be integers, got {type(item).__name__}"
                )
            result = container[item]
            return RonObject(result)
        else:
            raise TypeError(
                f"Value of type {type(val).__name__} is not subscriptable"
            )


@dataclass(frozen=True)
class RonStruct:
    name: str
    _fields: frozendict[RonValue, RonValue] | tuple[RonValue, ...]

    @property
    def as_dict(self) -> frozendict[RonValue, RonValue]:
        """Return dict or die"""
        if isinstance(self._fields, frozendict):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Tuple-Struct, not a Named-Struct"
        )

    @property
    def as_seq(self) -> tuple[RonValue, ...]:
        """Return tuple or die"""
        if isinstance(self._fields, tuple):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Named-Struct, not a Tuple-Struct"
        )


@dataclass(frozen=True)
class RonSeq:
    elements: tuple[RonValue, ...]
    kind: Literal["list", "tuple"]

    @property
    def as_seq(self) -> tuple[RonValue, ...]:
        return self.elements


@dataclass(frozen=True)
class RonMap:
    entries: frozendict[RonValue, RonValue]


@dataclass(frozen=True)
class RonOptional:
    value: RonValue | None


@dataclass(frozen=True)
class RonChar:
    value: str
