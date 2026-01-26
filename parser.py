from antlr4 import CommonTokenStream, InputStream

from models import RonValue
from ron_parser.RonLexer import RonLexer  # type: ignore
from ron_parser.RonParser import RonParser  # type: ignore
from visitor import RonConverter


class RonSyntaxError(Exception):
    pass


def parse_ron(data: str) -> RonValue:
    """
    Парсить рядок у форматі RON і повертає структуру Python об'єктів.
    """
    input_stream = InputStream(data)
    lexer = RonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = RonParser(stream)
    tree = parser.root()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise RonSyntaxError("Failed to parse RON data: Syntax Error")

    visitor = RonConverter()
    return visitor.visit(tree)
