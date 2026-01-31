import dataclasses
import typing
from dataclasses import is_dataclass

from frozendict import frozendict

from ron.models import (
    RonChar,
    RonMap,
    RonObject,
    RonOptional,
    RonSeq,
    RonStruct,
    RonValue,
)
from ron.parser import parse_ron


def from_ron[T](
    ron_val: RonObject | RonValue, target_type: typing.Type[T]
) -> T:
    """
    Function you can use to convert your `ron.models.RonObject` or
    `ron.models.RonValue` into your specific dataclass.

    >>> from dataclasses import dataclass
    >>> from ron import from_ron, parse_ron
    >>> @dataclass
    ... class Point:
    ...     x: int
    ...     y: int
    ...
    >>> obj = parse_ron("(x: 5, y: 13)")
    >>> point = from_ron(obj, Point)
    >>> point.x
    5
    >>> point.y
    13
    """
    if isinstance(ron_val, RonObject):
        ron_val = ron_val.v

    target_origin = typing.get_origin(target_type)
    target_args = typing.get_args(target_type)

    # 1) Turn RonOptional into Python's Optional[]
    if target_origin is typing.Union or (
        hasattr(typing, "UnionType")
        and isinstance(target_type, typing.UnionType)
    ):
        if isinstance(ron_val, RonOptional):
            match ron_val.value:
                case None:
                    return typing.cast(T, None)
                case v:
                    inner_type = next(
                        t for t in target_args if t is not type(None)
                    )
                    return from_ron(v, inner_type)

    # 2) Turn RonStruct into target's subclass
    #
    # Basically, enum handling
    if isinstance(ron_val, RonStruct) and not is_dataclass(target_type):
        for subclass in target_type.__subclasses__():
            if subclass.__name__ == ron_val.name:
                return from_ron(ron_val, subclass)
        raise ValueError(
            f"No subclass found for {ron_val.name} in {target_type}"
        )

    # 3) Turn RonStruct into target class
    #
    # Target type is supposed to be a dataclass
    if is_dataclass(target_type):
        if not isinstance(ron_val, RonStruct):
            raise TypeError(
                f"Expected RonStruct for {target_type}, got {type(ron_val)}"
            )

        if ron_val.name is not None and ron_val.name != target_type.__name__:
            raise ValueError(
                f"Name mismatch: RON '{ron_val.name}' vs Class '{target_type.__name__}'"
            )

        field_hints = typing.get_type_hints(target_type)
        kwargs = {}

        if isinstance(ron_val._fields, frozendict):
            # if it's a struct with named fields, map every target's field to
            # struct's field
            for field in dataclasses.fields(target_type):
                if field.name in ron_val._fields:
                    kwargs[field.name] = from_ron(
                        ron_val._fields[field.name],
                        field_hints[field.name],
                    )
            return target_type(**kwargs)
        elif isinstance(ron_val._fields, tuple):
            # if it's a struct with unnamed fields, just rely on order
            cls_fields = dataclasses.fields(target_type)
            for i, val in enumerate(ron_val._fields):
                f_name = cls_fields[i].name
                kwargs[f_name] = from_ron(val, field_hints[f_name])
            return target_type(**kwargs)

    # 4) Turn RonTuple/tuple into sequence target class
    if target_origin in (list, tuple, typing.Sequence):
        item_type = target_args[0] if target_args else typing.Any

        match ron_val:
            case RonSeq(elements):
                source_data = elements
            case _:
                raise RuntimeError(f"can't convert {ron_val} to sequence")

        return target_origin(from_ron(item, item_type) for item in source_data)

    # 5) Turn RonMap into dict target class
    if target_origin in (dict, typing.Mapping):
        key_type = target_args[0]
        item_type = target_args[1]

        assert isinstance(ron_val, RonMap), "can't convert {ron_val} to mapping"
        source_map = ron_val.entries.items()

        return target_origin(
            (from_ron(key, key_type), from_ron(item, item_type))
            for (key, item) in source_map
        )

    # 6) Turn primitives
    match ron_val:
        case RonChar(value):
            assert target_type is str, (
                f"tried to convert {ron_val!r} to {target_type}"
            )
            return typing.cast(T, value)
        case bool() | int() | float() | str():
            assert target_type in (int, float, str, bool), (
                f"tried to convert {ron_val!r} to {target_type}"
            )
            return typing.cast(T, ron_val)
        case other_val:
            raise RuntimeError(f"unexpected {other_val} to {target_type}")


class FromRonMixin:
    """
    Mixin that adds a capability to load a class from RON string
    """

    @classmethod
    def from_ron(cls, ron_string: str) -> typing.Self:
        """
        Load your type from a string.
        >>> from dataclasses import dataclass
        >>> from ron import FromRonMixin
        >>>
        >>> @dataclass
        ... class Point(FromRonMixin):
        ...     x: int
        ...     y: int
        ...
        >>> point = Point.from_ron("(x: 5, y: 13)")
        >>> point.x
        5
        >>> point.y
        13
        """
        parsed = parse_ron(ron_string)
        res = from_ron(parsed, cls)
        return res
