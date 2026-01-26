from antlr4 import CommonTokenStream, InputStream

from models import RonObject
from ron_parser.RonLexer import RonLexer  # type: ignore
from ron_parser.RonParser import RonParser  # type: ignore
from visitor import RonConverter


class RonSyntaxError(Exception):
    pass


def parse_ron(data: str) -> RonObject:
    """
    Парсить рядок у форматі RON і повертає структуру Python об'єктів.
    """
    input_stream = InputStream(data)
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

    visitor = RonConverter()
    return RonObject(visitor.visit(tree))
