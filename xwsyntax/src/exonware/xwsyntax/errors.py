#exonware/xwsyntax/src/exonware/xwsyntax/errors.py
"""
Exception hierarchy for the syntax module.
"""


class SyntaxError(Exception):
    """Base exception for syntax errors."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        if self.line is not None and self.column is not None:
            return f"{self.message} at line {self.line}, column {self.column}"
        elif self.line is not None:
            return f"{self.message} at line {self.line}"
        return self.message


class GrammarError(SyntaxError):
    """Error in grammar definition."""


class GrammarNotFoundError(GrammarError):
    """Grammar file not found."""


class ParseError(SyntaxError):
    """Error during parsing."""

    def __init__(
        self,
        message: str,
        text: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ):
        super().__init__(message, line, column)
        self.text = text


class ValidationError(SyntaxError):
    """Validation error."""


class MaxDepthError(SyntaxError):
    """Maximum parse depth exceeded."""
