import typing
from dataclasses import dataclass
from pprint import pprint
from typing import Any, cast

from antlr4 import CommonTokenStream, InputStream

from ron_parser.RonLexer import RonLexer
from ron_parser.RonParser import RonParser
from ron_parser.RonVisitor import RonVisitor

# --- Ваші структури даних ---

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


# --- Реалізація Visitor ---


class RonConverter(RonVisitor):
    @typing.override
    def visitRoot(self, ctx: RonParser.RootContext) -> RonValue:
        return cast(RonValue, self.visit(ctx.value()))

    # --- Обробка складних типів ---

    @typing.override
    def visitOptionValue(self, ctx: RonParser.OptionValueContext) -> RonOptional:
        # Отримуємо контекст правила option
        opt_ctx = ctx.option()

        # Перевіряємо, чи це None
        if opt_ctx.NONE():
            return RonOptional(value=None)

        # Якщо Some, беремо внутрішнє значення
        inner_value = cast(RonValue, self.visit(opt_ctx.value()))
        return RonOptional(value=inner_value)

    @typing.override
    def visitStructValue(self, ctx: RonParser.StructValueContext) -> RonStruct:
        struct_ctx = ctx.ron_struct()
        name = struct_ctx.IDENTIFIER().getText()

        # Перевіряємо тіло структури
        body = struct_ctx.struct_body()

        if body is None:
            # Unit struct: MyStruct
            return RonStruct(name=name, fields=[])

        if body.named_fields():
            # Named struct: MyStruct(a: 1, b: 2)
            fields: dict[str, RonValue] = {}
            for field in body.named_fields().named_field():
                key = field.IDENTIFIER().getText()
                val = cast(RonValue, self.visit(field.value()))
                fields[key] = val
            return RonStruct(name=name, fields=fields)

        elif body.unnamed_fields():
            # Tuple struct: MyStruct(1, 2)
            fields_list: list[RonValue] = []
            for val_ctx in body.unnamed_fields().value():
                fields_list.append(cast(RonValue, self.visit(val_ctx)))
            return RonStruct(name=name, fields=fields_list)

        return RonStruct(name=name, fields=[])

    @typing.override
    def visitMapValue(self, ctx: RonParser.MapValueContext) -> RonMap:
        map_ctx = ctx.ron_map()
        entries: dict[RonValue, RonValue] = {}
        # Проходимо по всіх map_entry
        for entry in map_ctx.map_entry():
            # entry children: [value (key), ':', value (val)]
            key = cast(RonValue, self.visit(entry.value(0)))
            val = cast(RonValue, self.visit(entry.value(1)))
            entries[key] = val
        return RonMap(entries=entries)

    @typing.override
    def visitTupleValue(self, ctx: RonParser.TupleValueContext) -> RonTuple:
        tuple_ctx = ctx.ron_tuple()
        elements: list[RonValue] = [
            cast(RonValue, self.visit(v)) for v in tuple_ctx.value()
        ]
        return RonTuple(elements=elements)

    @typing.override
    def visitListValue(self, ctx: RonParser.ListValueContext) -> list[RonValue]:
        # RON list [a, b] -> Python list
        list_ctx = ctx.ron_list()
        if not list_ctx.value():
            return []
        return [cast(RonValue, self.visit(v)) for v in list_ctx.value()]

    # --- Обробка примітивів ---

    @typing.override
    def visitIntValue(self, ctx: RonParser.IntValueContext) -> int:
        text = ctx.getText()
        # Автоматичне визначення бази (0x, 0b, etc.)
        return int(text, 0)

    @typing.override
    def visitFloatValue(self, ctx: RonParser.FloatValueContext) -> float:
        return float(ctx.getText())

    @typing.override
    def visitBoolValue(self, ctx: RonParser.BoolValueContext) -> bool:
        return ctx.getText() == "true"

    @typing.override
    def visitStringValue(self, ctx: RonParser.StringValueContext) -> str:
        raw_text = ctx.getText()
        # Проста обробка: видаляємо лапки.
        if raw_text.startswith("r"):
            # Raw string r#"..."#
            hash_count = 0
            while raw_text[1 + hash_count] == "#":
                hash_count += 1
            return raw_text[2 + hash_count : -(1 + hash_count)]
        else:
            # Normal string "..."
            # type: ignore - decode exists on bytes, inferred correctly but strict checkers might complain on chaining
            return raw_text[1:-1].encode("utf-8").decode("unicode_escape")

    @typing.override
    def visitCharValue(self, ctx: RonParser.CharValueContext) -> RonChar:
        # 'c' -> c
        return RonChar(value=ctx.getText()[1:-1])


# --- Helper для запуску ---


def parse_ron_string(ron_data: str) -> RonValue:
    input_stream = InputStream(ron_data)
    lexer = RonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = RonParser(stream)

    # Запускаємо парсинг з правила root
    tree = parser.root()

    # Якщо були помилки синтаксису, кидаємо виключення
    if parser.getNumberOfSyntaxErrors() > 0:
        raise Exception("Syntax Error in RON data")

    visitor = RonConverter()
    return visitor.visit(tree)


# --- Тестування ---

if __name__ == "__main__":
    ron_sample = r"""
    Scene(
        entities: {
            "hero": Entity(
                pos: (10, 20),
                active: true,
                meta: None
            ),
            "monster": Entity(
                pos: (50, -5),
                active: false,
                meta: Some("Boss")
            )
        },
        settings: [1, 2, 3],
        id: 42
    )
    """

    try:
        result = parse_ron_string(ron_sample)
        print("Parsed Result:")
        pprint(result)

        if isinstance(result, RonStruct) and isinstance(result.fields, dict):
            entities: list[Any] = result.fields.get("entities")
            hero = entities.entries["hero"]
            pprint(entities)
    except Exception as e:
        print(e)
