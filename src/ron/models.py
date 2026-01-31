"""
High-level utilities for traversing and manipulating Rusty Object Notation (RON)
data.

This module features `RonObject` and semi-internal parser types (`RonValue`).
Although it is possible to use primitive syntax types directly, you will likely
prefer using `RonObject`'s `__getitem__` implementation, especially for nested
lookups. It abstracts away specific key and container types, allowing you to use
plain Python objects to access the data.

To access the raw syntax leaves, `RonObject` exposes a family of `expect_`
methods (e.g., `expect_int`, `expect_map`).

These methods assert that the value
matches the expected type, raising a `ValueError` if it does not (which also
makes type checkers happy).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, TypeGuard, override

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
"""
@public Union of all supported RON types, including primitives and containers.
"""


def is_ron_value(val: Any) -> TypeGuard[RonValue]:
    """
    Type-guard that checks that your value is indeed of `RonValue`

    Use with typecheckers.
    """
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
    """
    A wrapper around `RonValue` enabling convenient traversal.

    It allows you to access nested fields using standard Python types as keys,
    automatically handling the necessary conversions to RON-specific types.

    Read `RonObject.__getitem__`() docs for more.
    """

    v: RonValue
    """@private field holding the internal value"""

    def expect_map(self) -> RonMap:
        """Returns an underlying map or **raises** a `ValueError`"""
        if isinstance(self.v, RonMap):
            return self.v
        raise ValueError(f"Value '{self}' is not a map")

    def expect_struct(self) -> RonStruct:
        """Returns an underlying struct or **raises** a `ValueError`"""
        if isinstance(self.v, RonStruct):
            return self.v
        raise ValueError(f"Value '{self}' is not a struct")

    def expect_int(self) -> int:
        """Returns an underlying int or **raises** a `ValueError`"""
        if isinstance(self.v, int):
            return self.v
        raise ValueError(f"Value '{self}' is not an integer")

    def expect_float(self) -> float:
        """Returns an underlying float or **raises** a `ValueError`"""
        if isinstance(self.v, float):
            return self.v
        raise ValueError(f"Value '{self}' is not a float")

    def expect_str(self) -> str:
        """Returns an underlying str or **raises** a `ValueError`"""
        if isinstance(self.v, str):
            return self.v
        raise ValueError(f"Value '{self}' is not a string")

    def expect_bool(self) -> bool:
        """Returns an underlying bool or **raises** a `ValueError`"""
        if isinstance(self.v, bool):
            return self.v
        raise ValueError(f"Value '{self}' is not a boolean")

    def expect_tuple(self) -> RonSeq:
        """Returns an underlying tuple or **raises** a `ValueError`"""
        if isinstance(self.v, RonSeq) and self.v.kind == "tuple":
            return self.v
        raise ValueError(f"Value '{self}' is not a ron tuple")

    def expect_list(self) -> RonSeq:
        """Returns an underlying list or **raises** a `ValueError`"""
        if isinstance(self.v, RonSeq) and self.v.kind == "list":
            return self.v
        raise ValueError(f"Value '{self}' is not a ron list")

    def maybe(self) -> RonObject | None:
        """
        Transposes a RON optional into Python `Optional`.

        # Returns
        `RonObject` | `None`: The inner value, if present.

        # Raises
        - `ValueError`: If the value is not an option.

        Examples:
        >>> from ron import parse_ron
        >>> obj = parse_ron('Some(42)')
        >>> result = obj.maybe()
        >>> assert result is not None
        >>> result.expect_int()
        42

        >>> obj = parse_ron('None')
        >>> obj.maybe() is None
        True

        >>> # Raises error if called on non-option types
        >>> obj = parse_ron('42')
        >>> obj.maybe()
        Traceback (most recent call last):
            ...
        ValueError: Value ... is not an option
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
        | None
        | RonObject,
    ) -> RonObject:
        """
        @public Escape hatch to traverse the RON object.

        This method inspects the underlying container (Map, Struct, or Sequence)
        and (if needed) automatically converts the provided `item` into the
        correct RON type required for the lookup.

        For example, passing a `str` to a struct will look up that field name,
        and passing a `tuple` to a map will convert it to a `RonSeq` key.

        # Returns
        `RonObject`: A new wrapper around the retrieved value, enabling
        chained access.

        # Raises
        - `TypeError`: If the value is not a container, or if the key type
            is invalid for the current container.
        - `KeyError`: If the item is missing (for Maps and Structs).
        - `IndexError`: If the index is out of bounds (for Sequences).

        Examples:
        >>> from ron import parse_ron

        >>> # Struct access: use string keys for field names
        >>> obj = parse_ron('( id: 42, name: "foo" )')
        >>> obj["id"].expect_int()
        42

        >>> # Map access: use standard Python literals
        >>> obj = parse_ron('{ "key": "value" }')
        >>> obj["key"].expect_str()
        'value'

        >>> # Sequence access: use integer indices
        >>> obj = parse_ron('[10, 20, 30]')
        >>> obj[1].expect_int()
        20

        >>> # Complex keys: Python tuples are automatically coerced to RON tuples
        >>> obj = parse_ron('{ (1, "a"): "found" }')
        >>> obj[(1, "a")].expect_str()
        'found'

        >>> # Nested chaining
        >>> obj = parse_ron('( config: (version: 1) )')
        >>> obj["config"]["version"].expect_int()
        1

        >>> # Unit structs
        >>> obj = parse_ron('{ King: "Crown" }')
        >>> obj["King"].expect_str()
        'Crown'

        >>> # And even optionals
        >>> obj = parse_ron('{ Some("King"): "Crown", None: "Hat" }')
        >>> obj["King"].expect_str()
        'Crown'
        >>> obj[None].expect_str()
        'Hat'

        >>> # Nested coercion doesn't work for now
        >>> obj = parse_ron('{ Some(King): "Crown", None: "Hat" }')
        >>> obj["King"].expect_str() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        KeyError: ... coerced as Some("King"), not Some(King)

        >>> # If you need nested keys, parse them
        >>> obj[parse_ron("Some(King)")].expect_str()
        'Crown'
        """

        val = self.v
        if isinstance(item, RonObject):
            item = item.v

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

        # Handle optionals and unit structs
        if type(key) is RonOptional and type(item) is not RonOptional:
            item = RonOptional(item)
        elif type(key) is RonStruct and type(item) is str:
            item = RonStruct(item, _fields=tuple(), spans=None)
        elif item is None:
            item = RonOptional(None)

        # 3. Do the index magic and wrap in RonObject to prolong the chain
        if isinstance(container, frozendict):
            try:
                result = container[item]
            except (KeyError, TypeError):
                raise KeyError(
                    f"container={container}, key={item}, heuristic_key={key}"
                )
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
    """
    Represents span point, the beginning or the end of the element.
    """

    ch: int
    """
    Character index in a stream
    """
    line: int
    """
    Line number, starts at 1
    """
    column: int
    """
    Column number, starts at 1
    """


type Span = tuple[SpanPoint, SpanPoint]
"""
@private
"""


@dataclass(frozen=True)
class RonStruct:
    """
    Represents RON structures.

    Includes:
    - named structs like `Weapon(str: 5)`
    - anon structs like `(str: 5)`
    - structs with named fields (see above)
    - structs with unnamed fields like `Weapon(5)`
    - unit structs like ... `Weapon`?
    - enums like `RBG(r: 255, g: 0, b: 0)` (yes, same syntax as structs)
    - unit enums like `Red` (more useful than unit structs)

    Use `RonStruct.as_dict` or `RonStruct.as_tuple` to get fields.

    **Careful**, they will panic if you try to get the wrong thing.

    And if you, for some reason, need a name, there's `RonStruct.name`
    (might be `None`).


    Oh, and it has spans. See `RonStruct.spans`.
    """

    name: str | None
    """
    Struct's name, if present. Simple as that.
    """
    _fields: frozendict[RonValue, RonValue] | tuple[RonValue, ...]
    """
    @private
    """

    spans: frozendict[RonValue, Span] | tuple[Span, ...] | None
    """
    Represents spans for struct field *values* as (start, end).
    See `SpanPoint`.
    """

    @property
    def as_dict(self) -> frozendict[RonValue, RonValue]:
        """Returns the underlying dictionary for structs with named fields.

        **Raises** a `ValueError` otherwise.
        """
        if isinstance(self._fields, frozendict):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Tuple-Struct, not a Named-Struct"
        )

    @property
    def as_tuple(self) -> tuple[RonValue, ...]:
        """Returns the underlying tuple for structs with unnamed fields.

        **Raises** a ValueError otherwise.
        """
        if isinstance(self._fields, tuple):
            return self._fields
        raise ValueError(
            f"Struct '{self.name}' is a Named-Struct, not a Tuple-Struct"
        )


@dataclass(frozen=True)
class RonSeq:
    """
    Represents all sort of sequences: tuple `()`, lists `[]`, sets `[]`.

    Use `RonSeq.as_tuple` to get said sequence as a `tuple`.

    If you need such info, for some reason, you can use `RonSeq.kind` to
    find out whether it was parsed from `()` or `[]`.
    """

    elements: tuple[RonValue, ...]
    """
    @private
    """

    kind: Literal["list", "tuple"]

    @property
    def as_tuple(self) -> tuple[RonValue, ...]:
        """Returns the underlying sequence as a tuple."""
        return self.elements


@dataclass(frozen=True)
class RonMap:
    """
    Represents a RON map, you can think of it as python's dict pretty much.

    Use `RonMap.as_dict` to get said dict as `frozendict`
    """

    entries: frozendict[RonValue, RonValue]
    """
    @private
    """

    @property
    def as_dict(self) -> frozendict[RonValue, RonValue]:
        """Returns the underlying mapping as a `frozendict`."""
        return self.entries


@dataclass(frozen=True)
class RonOptional:
    """
    Represents things like `Some("value")` or None.

    Unlike in Python, that's a real object, but feel free to snatch it
    with `RonOptional.value`.

    Or use fancy methods to work with the object like `RonOptional.map`.
    """

    value: RonValue | None

    def unwrap(self) -> RonValue:
        """
        Asserts that value is present, and returns it.

        **Raises** a `ValueError` otherwise.
        """
        if self.value is None:
            raise ValueError("tried to call unwrap() on None value")
        return self.value

    def unwrap_or(self, o: RonValue) -> RonValue:
        """
        Return a value if present, or return a fallback.
        """
        if self.value is None:
            return o
        return self.value

    def map(self, f: Callable[[RonValue], RonValue]):
        """
        Apply a function to the underlying value, if present.

        If not, nothing happens.
        """
        if self.value is None:
            return None
        return f(self.value)


@dataclass(frozen=True)
class RonChar:
    """
    Represents characters, like 'a'.
    """

    value: str

    @override
    def __str__(self) -> str:
        return self.value
