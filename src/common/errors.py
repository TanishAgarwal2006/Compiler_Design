"""
Central error-reporting module for lexical, syntax, and semantic errors.
"""

lex_errors: list[str] = []
syntax_errors: list[str] = []
semantic_errors: list[str] = []


def add_lex_error(message: str) -> None:
    lex_errors.append(message)


def add_syntax_error(message: str) -> None:
    syntax_errors.append(message)


def add_semantic_error(message: str) -> None:
    semantic_errors.append(message)


def clear_errors() -> None:
    lex_errors.clear()
    syntax_errors.clear()
    semantic_errors.clear()


def has_errors() -> bool:
    return bool(lex_errors or syntax_errors or semantic_errors)
