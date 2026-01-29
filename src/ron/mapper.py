import typing
from dataclasses import fields, is_dataclass

from frozendict import frozendict

from ron.models import RonChar, RonMap, RonOptional, RonStruct, RonTuple


def from_ron(ron_val: typing.Any, target_type: typing.Type):
    """
    Рекурсивно конвертує об'єкти моделей RON у вказаний Python тип.
    """
    # 1. Обробка Optional[T] (Union[T, None])
    origin = typing.get_origin(target_type)
    args = typing.get_args(target_type)

    if origin is typing.Union or (
        hasattr(typing, "UnionType")
        and isinstance(target_type, typing.UnionType)
    ):
        if isinstance(ron_val, RonOptional):
            if ron_val.value is None:
                return None
            # Шукаємо в Union тип, який не є None
            inner_type = next(t for t in args if t is not type(None))
            return from_ron(ron_val.value, inner_type)
        if ron_val is None:
            return None

    # 2. Обробка "Rust-style" Enum (ієрархія класів)
    # Якщо прийшла структура, а target_type має підкласи
    if isinstance(ron_val, RonStruct) and not is_dataclass(target_type):
        for subclass in target_type.__subclasses__():
            if subclass.__name__ == ron_val.name:
                return from_ron(ron_val, subclass)
        raise ValueError(
            f"No subclass found for {ron_val.name} in {target_type}"
        )

    # 3. Обробка Dataclasses
    if is_dataclass(target_type):
        if not isinstance(ron_val, RonStruct):
            raise TypeError(
                f"Expected RonStruct for {target_type}, got {type(ron_val)}"
            )

        if ron_val.name != target_type.__name__:
            raise ValueError(
                f"Name mismatch: RON '{ron_val.name}' vs Class '{target_type.__name__}'"
            )

        field_hints = typing.get_type_hints(target_type)
        kwargs = {}

        # Обробка іменованих полів
        if isinstance(ron_val._fields, frozendict):
            for field in fields(target_type):
                if field.name in ron_val._fields:
                    kwargs[field.name] = from_ron(
                        ron_val._fields[field.name],
                        field_hints[field.name],
                    )
        # Обробка неіменованих полів (Tuple Struct)
        elif isinstance(ron_val._fields, tuple):
            cls_fields = fields(target_type)
            for i, val in enumerate(ron_val._fields):
                f_name = cls_fields[i].name
                kwargs[f_name] = from_ron(val, field_hints[f_name])

        return target_type(**kwargs)

    # 4. Обробка колекцій (list, tuple)
    if origin in (list, tuple, typing.Sequence):
        item_type = args[0] if args else typing.Any
        # RON списки ми зберігаємо як tuple
        source_data = (
            ron_val.elements if isinstance(ron_val, RonTuple) else ron_val
        )
        return origin(from_ron(item, item_type) for item in source_data)

    # 5. Базові типи та примітиви
    if isinstance(ron_val, RonChar):
        return ron_val.value

    return ron_val
