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

    def __getitem__(
        self,
        item: RonValue
        | tuple[RonValue, ...]
        | list[RonValue]
        | dict[Any, Any]
        | None,
    ) -> "RonObject":
        val = self.v

        # 1. Pick a proper container (and its key type)
        key = None
        if isinstance(val, RonStruct):
            container = val._fields
            if type(container) is frozendict:
                key = container.key(0)
        elif isinstance(val, RonMap):
            container = val.entries
            key = container.key(0)
        elif isinstance(val, RonSeq):
            container = val.elements
        elif isinstance(val, tuple):
            container = val
        else:
            raise TypeError(f"{self}[{item}]")

        # 2. Convert index to a proper ron type, if needed
        if isinstance(item, tuple):
            match key:
                case RonSeq():
                    item = RonSeq(elements=item, kind="tuple")
                case RonStruct(name):
                    item = RonStruct(name, _fields=item, spans=None)
                case _:
                    raise TypeError(f"{self}[{item}]: Unexpected index type")
        if isinstance(item, list):
            item = RonSeq(elements=tuple(item), kind="list")
        if isinstance(item, dict):
            match key:
                case RonMap():
                    item = RonMap(entries=frozendict(item))
                case RonStruct(name):
                    item = RonStruct(name, _fields=frozendict(item), spans=None)
                case _:
                    raise TypeError(f"{self}[{item}]: Unexpected index type")
        if type(key) is RonOptional:
            item = RonOptional(item)
        if type(key) is RonStruct and type(item) is str:
            item = RonStruct(item, _fields=tuple(), spans=None)
        if item is None:
            item = RonOptional(None)

        # 3. Do the index magic and wrap in RonObject to prolong the chain
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
class SpanPoint:
    ch: int
    line: int
    column: int


type Span = tuple[SpanPoint, SpanPoint]


@dataclass(frozen=True)
class RonStruct:
    name: str | None
    _fields: frozendict[RonValue, RonValue] | tuple[RonValue, ...]
    spans: frozendict[RonValue, Span] | tuple[Span, ...] | None

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
