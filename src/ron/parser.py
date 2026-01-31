import typing

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from ron._generated.RonLexer import RonLexer  # type: ignore
from ron._generated.RonParser import RonParser  # type: ignore
from ron.models import RonObject, is_ron_value
from ron.visitor import RonConverter


class RonErrorListener(ErrorListener):
    @typing.override
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ValueError(f"RON Syntax Error at line {line}:{column} -> {msg}")


class RonSyntaxError(Exception):
    pass


def parse_ron(src_text: str, *, with_spans: bool = False) -> RonObject:
    """
    Parses the string and returns a `ron.models.RonObject`.
    """
    input_stream = InputStream(src_text)
    lexer = RonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    # stream.fill()
    #
    # for token in stream.tokens:
    #     print(f"Token: {token.type} -> '{token.text}'")
    parser = RonParser(stream)
    tree = parser.root()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise RonSyntaxError("Failed to parse RON data: Syntax Error")

    line_index = [0] + [
        i + 1 for i, char in enumerate(src_text) if char == "\n"
    ]
    visitor = RonConverter(with_spans=with_spans, line_index=line_index)
    val = visitor.visit(tree)  # type: ignore
    assert is_ron_value(val), f"visitor returned {val} :/"

    return RonObject(val)
