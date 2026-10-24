"""Error lists shared by every compiler stage, and one printer for all of them.

Each stage appends a plain message string. `format_errors` turns the strings
into one uniform layout:

    prog.c:4: syntax error: unexpected token 'return' (is a ';' missing ...)
        4 |     return 0;
"""
import re

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


_PREFIX = re.compile(r"^(Lexical Error: |Syntax Error: |semantic error at line \d+: )")
_LINE = re.compile(r"line (\d+)")
_TAIL = re.compile(r" at line \d+$")


def _split(message: str) -> tuple[int | None, str]:
    """Return (line number or None, message without the stage prefix and line tail)."""
    found = _LINE.search(message)
    text = _TAIL.sub("", _PREFIX.sub("", message))
    return (int(found.group(1)) if found else None), text


def format_errors(filename: str, source: str) -> str:
    """All collected errors, sorted by line, duplicates removed, with source lines."""
    rows = []
    for kind, errs in (("lexical", lex_errors), ("syntax", syntax_errors), ("semantic", semantic_errors)):
        rows += [(*_split(e), kind) for e in errs]
    rows = sorted(set(rows), key=lambda r: (r[0] or 0, r[2], r[1]))
    lines = source.split("\n")
    out = []
    for line, text, kind in rows:
        out.append(f"{filename}:{line or '?'}: {kind} error: {text}")
        if line and 1 <= line <= len(lines):
            out.append(f"  {line:4d} | {lines[line - 1].rstrip()}")
    out.append(f"{len(rows)} error{'s' if len(rows) != 1 else ''} found. No output was produced.")
    return "\n".join(out)
