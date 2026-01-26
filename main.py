import sys
from dataclasses import dataclass
from pprint import pprint

from antlr4 import *

# Імпортуємо згенеровані класи з папки ron_parser
from ron_parser.RonLexer import RonLexer
from ron_parser.RonParser import RonParser
from ron_parser.RonVisitor import RonVisitor

# --- Ваші структури даних ---

type RonValue = "RonStruct | RonTuple | RonMap | RonOptional | RonChar | int | float | str | bool | list[RonValue]"


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
    def visitRoot(self, ctx: RonParser.RootContext):
        return self.visit(ctx.value())

    # --- Обробка складних типів ---

    def visitOptionValue(self, ctx: RonParser.OptionValueContext):
        # Отримуємо контекст правила option
        opt_ctx = ctx.option()

        # Перевіряємо, чи це None (токен NONE існує?)
        if opt_ctx.NONE():
            return RonOptional(value=None)

        # Якщо Some, беремо внутрішнє значення
        inner_value = self.visit(opt_ctx.value())
        return RonOptional(value=inner_value)

    def visitStructValue(self, ctx: RonParser.StructValueContext):
        struct_ctx = ctx.ron_struct()
        name = struct_ctx.IDENTIFIER().getText()

        # Перевіряємо тіло структури
        body = struct_ctx.struct_body()

        if body is None:
            # Unit struct: MyStruct
            return RonStruct(name=name, fields=[])

        if body.named_fields():
            # Named struct: MyStruct(a: 1, b: 2)
            fields = {}
            for field in body.named_fields().named_field():
                key = field.IDENTIFIER().getText()
                val = self.visit(field.value())
                fields[key] = val
            return RonStruct(name=name, fields=fields)

        elif body.unnamed_fields():
            # Tuple struct: MyStruct(1, 2)
            fields = []
            for val_ctx in body.unnamed_fields().value():
                fields.append(self.visit(val_ctx))
            return RonStruct(name=name, fields=fields)

        return RonStruct(name=name, fields=[])

    def visitMapValue(self, ctx: RonParser.MapValueContext):
        map_ctx = ctx.ron_map()
        entries = {}
        # Проходимо по всіх map_entry
        for entry in map_ctx.map_entry():
            # entry children: [value (key), ':', value (val)]
            key = self.visit(entry.value(0))
            val = self.visit(entry.value(1))
            entries[key] = val
        return RonMap(entries=entries)

    def visitTupleValue(self, ctx: RonParser.TupleValueContext):
        tuple_ctx = ctx.ron_tuple()
        elements = [self.visit(v) for v in tuple_ctx.value()]
        return RonTuple(elements=elements)

    def visitListValue(self, ctx: RonParser.ListValueContext):
        # RON list [a, b] -> Python list
        list_ctx = ctx.ron_list()
        if not list_ctx.value():
            return []
        return [self.visit(v) for v in list_ctx.value()]

    # --- Обробка примітивів ---

    def visitIntValue(self, ctx: RonParser.IntValueContext):
        text = ctx.getText()
        # Автоматичне визначення бази (0x, 0b, etc.)
        return int(text, 0)

    def visitFloatValue(self, ctx: RonParser.FloatValueContext):
        return float(ctx.getText())

    def visitBoolValue(self, ctx: RonParser.BoolValueContext):
        return ctx.getText() == "true"

    def visitStringValue(self, ctx: RonParser.StringValueContext):
        raw_text = ctx.getText()
        # Проста обробка: видаляємо лапки.
        # Для повного продакшн коду тут потрібен unescape
        if raw_text.startswith("r"):
            # Raw string r#"..."#
            hash_count = 0
            while raw_text[1 + hash_count] == "#":
                hash_count += 1
            return raw_text[2 + hash_count : -(1 + hash_count)]
        else:
            # Normal string "..."
            return raw_text[1:-1].encode("utf-8").decode("unicode_escape")

    def visitCharValue(self, ctx: RonParser.CharValueContext):
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

        # Перевірка доступу до полів
        hero = result.fields["entities"].entries["hero"]
        print(f"\nHero Position: {hero.fields['pos'].elements}")
        print(f"Hero Meta: {hero.fields['meta']}")

    except Exception as e:
        print(e)
