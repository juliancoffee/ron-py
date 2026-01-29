# Generated from Ron.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .RonParser import RonParser
else:
    from RonParser import RonParser

# This class defines a complete generic visitor for a parse tree produced by RonParser.

class RonVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RonParser#root.
    def visitRoot(self, ctx:RonParser.RootContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#OptionValue.
    def visitOptionValue(self, ctx:RonParser.OptionValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#StructValue.
    def visitStructValue(self, ctx:RonParser.StructValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#MapValue.
    def visitMapValue(self, ctx:RonParser.MapValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#TupleValue.
    def visitTupleValue(self, ctx:RonParser.TupleValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ListValue.
    def visitListValue(self, ctx:RonParser.ListValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#CharValue.
    def visitCharValue(self, ctx:RonParser.CharValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#StringValue.
    def visitStringValue(self, ctx:RonParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#FloatValue.
    def visitFloatValue(self, ctx:RonParser.FloatValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#IntValue.
    def visitIntValue(self, ctx:RonParser.IntValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#BoolValue.
    def visitBoolValue(self, ctx:RonParser.BoolValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#option.
    def visitOption(self, ctx:RonParser.OptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ron_anon_struct.
    def visitRon_anon_struct(self, ctx:RonParser.Ron_anon_structContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#strict_struct_body.
    def visitStrict_struct_body(self, ctx:RonParser.Strict_struct_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ron_struct.
    def visitRon_struct(self, ctx:RonParser.Ron_structContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#struct_body.
    def visitStruct_body(self, ctx:RonParser.Struct_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#named_fields.
    def visitNamed_fields(self, ctx:RonParser.Named_fieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#named_field.
    def visitNamed_field(self, ctx:RonParser.Named_fieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#unnamed_fields.
    def visitUnnamed_fields(self, ctx:RonParser.Unnamed_fieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ron_map.
    def visitRon_map(self, ctx:RonParser.Ron_mapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#map_entry.
    def visitMap_entry(self, ctx:RonParser.Map_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ron_tuple.
    def visitRon_tuple(self, ctx:RonParser.Ron_tupleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RonParser#ron_list.
    def visitRon_list(self, ctx:RonParser.Ron_listContext):
        return self.visitChildren(ctx)



del RonParser