from typing import cast

from frozendict import frozendict

from ron._generated.RonParser import RonParser  # type: ignore
from ron._generated.RonVisitor import RonVisitor  # type: ignore
from ron.models import RonChar, RonMap, RonOptional, RonSeq, RonStruct, RonValue


class RonConverter(RonVisitor):
    def visitRoot(self, ctx: RonParser.RootContext) -> RonValue:
        return cast(RonValue, self.visit(ctx.value()))

    def visitOptionValue(
        self, ctx: RonParser.OptionValueContext
    ) -> RonOptional:
        opt_ctx = ctx.option()
        if opt_ctx.NONE():
            return RonOptional(value=None)
        inner_value = cast(RonValue, self.visit(opt_ctx.value()))
        return RonOptional(value=inner_value)

    def visitStructValue(self, ctx: RonParser.StructValueContext) -> RonStruct:
        if ctx.ron_struct() is not None:
            struct_ctx = ctx.ron_struct()
            name = struct_ctx.IDENTIFIER().getText()
            body = struct_ctx.struct_body()
        elif ctx.ron_anon_struct() is not None:
            struct_ctx = ctx.ron_anon_struct()
            name = None
            body = struct_ctx.strict_struct_body()
        else:
            raise RuntimeError("structValue is invalid")

        if body is None:
            return RonStruct(name=name, _fields=tuple())

        if body.named_fields():
            fields: dict[RonValue, RonValue] = {}
            for field in body.named_fields().named_field():
                key = field.IDENTIFIER().getText()
                val = cast(RonValue, self.visit(field.value()))
                fields[key] = val

            return RonStruct(
                name=name,
                _fields=frozendict(fields),
            )

        elif body.unnamed_fields():
            fields_list: list[RonValue] = []
            for val_ctx in body.unnamed_fields().value():
                fields_list.append(cast(RonValue, self.visit(val_ctx)))

            return RonStruct(name=name, _fields=tuple(fields_list))

        return RonStruct(name=name, _fields=tuple())

    def visitMapValue(self, ctx: RonParser.MapValueContext) -> RonMap:
        map_ctx = ctx.ron_map()
        entries: dict[RonValue, RonValue] = {}
        for entry in map_ctx.map_entry():
            key = cast(RonValue, self.visit(entry.value(0)))
            val = cast(RonValue, self.visit(entry.value(1)))
            entries[key] = val
        return RonMap(entries=frozendict() | entries)

    def visitTupleValue(self, ctx: RonParser.TupleValueContext) -> RonSeq:
        tuple_ctx = ctx.ron_tuple()
        elements = tuple(
            cast(RonValue, self.visit(v)) for v in tuple_ctx.value()
        )
        return RonSeq(elements=elements, kind="tuple")

    def visitListValue(self, ctx: RonParser.ListValueContext) -> RonSeq:
        list_ctx = ctx.ron_list()
        if not list_ctx.value():
            return RonSeq(elements=tuple(), kind="list")
        return RonSeq(
            tuple(cast(RonValue, self.visit(v)) for v in list_ctx.value()),
            kind="list",
        )

    def visitIntValue(self, ctx: RonParser.IntValueContext) -> int:
        return int(ctx.getText(), 0)

    def visitFloatValue(self, ctx: RonParser.FloatValueContext) -> float:
        return float(ctx.getText())

    def visitBoolValue(self, ctx: RonParser.BoolValueContext) -> bool:
        return ctx.getText() == "true"

    def visitStringValue(self, ctx: RonParser.StringValueContext) -> str:
        raw_text = ctx.getText()
        if raw_text.startswith("r"):
            hash_count = 0
            while raw_text[1 + hash_count] == "#":
                hash_count += 1
            return raw_text[2 + hash_count : -(1 + hash_count)]
        else:
            return raw_text[1:-1].encode("utf-8").decode("unicode_escape")

    def visitCharValue(self, ctx: RonParser.CharValueContext) -> RonChar:
        raw_text = ctx.getText()
        encoded = raw_text[1:-1].encode("utf-8").decode("unicode_escape")

        return RonChar(value=encoded)
