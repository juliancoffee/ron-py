from __future__ import annotations

from dataclasses import dataclass

from frozendict import frozendict

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
    | tuple["RonValue", ...]
)


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

    def expect_tuple(self) -> RonTuple:
        if isinstance(self.v, RonTuple):
            return self.v
        raise ValueError(f"Value '{self}' is not a ron tuple")

    def expect_list(self) -> tuple[RonValue, ...]:
        if isinstance(self.v, tuple):
            return self.v
        raise ValueError(f"Value '{self}' is not a tuple")

    def into_option(self) -> "RonObject" | None:
        if isinstance(self.v, RonOptional):
            return RonObject(self.v.value) if self.v.value is not None else None
        raise ValueError(f"Value '{self}' is not an option")

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

        if isinstance(container, frozendict):
            result = container[item]  # type: ignore
        elif isinstance(container, tuple):
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
    def as_list(self) -> tuple[RonValue, ...]:
        """Return tuple or die"""
        if isinstance(self._fields, tuple):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Named-Struct, not a Tuple-Struct"
        )


@dataclass(frozen=True)
class RonTuple:
    elements: tuple[RonValue, ...]


@dataclass(frozen=True)
class RonMap:
    entries: frozendict[RonValue, RonValue]


@dataclass(frozen=True)
class RonOptional:
    value: RonValue | None


@dataclass(frozen=True)
class RonChar:
    value: str
