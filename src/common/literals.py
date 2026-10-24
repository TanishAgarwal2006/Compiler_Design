"""
Literal helpers for the semantic and TAC phases.

The lexer keeps character and string literals as raw source text, quotes and
escape sequences included (for example ``'\\n'`` or ``"hi\\n"``); integer,
float and bool literals arrive already converted by the parser. Later phases
need real values, so this module turns literal text into numbers and bytes.

Escapes (the same in characters and strings, checked by the lexer):
n r t b f v a ? \\ ' ", octal ``\\ooo`` (1 to 3 digits) and hex ``\\xHH...``.
"""
import re
from typing import Any

SIMPLE_ESCAPES = {
    "n": 10, "r": 13, "t": 9, "b": 8, "f": 12, "v": 11,
    "a": 7, "?": 63, "\\": 92, "'": 39, '"': 34,
}

# One valid escape sequence starting at a backslash.
ESCAPE = re.compile(r"\\(?:[ntrabfv?\\'\"]|[0-7]{1,3}|x[0-9a-fA-F]+)")


def escape_value(seq: str) -> int:
    """Value of one valid escape sequence such as ``\\n``, ``\\101`` or ``\\x41``."""
    body = seq[1:]
    if body[0] == "x":
        return int(body[1:], 16) & 0xFF
    if body[0] in "01234567":
        return int(body, 8) & 0xFF
    return SIMPLE_ESCAPES[body]


def bad_escapes(inner: str) -> list[str]:
    """Return every invalid escape sequence inside the text of a literal."""
    bad, i = [], 0
    while i < len(inner):
        if inner[i] != "\\":
            i += 1
            continue
        m = ESCAPE.match(inner, i)
        if m:
            i = m.end()
        else:
            bad.append(inner[i:i + 2])
            i += 2
    return bad


def char_value(text: str) -> int:
    """Return the integer code of a character literal such as ``'a'`` or ``'\\n'``."""
    if len(text) < 3 or text[0] != "'" or text[-1] != "'":
        raise ValueError(f"not a character literal: {text!r}")
    inner = text[1:-1]
    if inner.startswith("\\"):
        m = ESCAPE.fullmatch(inner)
        if not m:
            raise ValueError(f"invalid escape in character literal: {text!r}")
        value = escape_value(inner)
    elif len(inner) != 1:
        raise ValueError(f"multi-character constant: {text!r}")
    else:
        value = ord(inner)
    return value - 256 if value > 127 else value     # char is signed 8-bit


def string_bytes(text: str) -> bytes:
    """Return the bytes of a string literal (no trailing NUL) with escapes resolved."""
    if len(text) < 2 or text[0] != '"' or text[-1] != '"':
        raise ValueError(f"not a string literal: {text!r}")
    inner = text[1:-1]
    out = bytearray()
    i = 0
    while i < len(inner):
        if inner[i] != "\\":
            out += inner[i].encode("utf-8")
            i += 1
            continue
        m = ESCAPE.match(inner, i)
        if not m:
            raise ValueError(f"invalid escape sequence in string literal: {text!r}")
        out.append(escape_value(m.group()))
        i = m.end()
    return bytes(out)


def literal_value(node: Any) -> Any:
    """Return the Python value of a ``Literal`` AST node.

    int -> int, float -> float, char -> int code, bool -> 0 or 1,
    string -> bytes (without the terminating NUL).
    """
    kind = node.literal_type
    if kind == "int":
        return int(node.value)
    if kind == "float":
        return float(node.value)
    if kind == "char":
        return char_value(node.value)
    if kind == "bool":
        return 1 if str(node.value) == "true" else 0
    if kind == "string":
        return string_bytes(node.value)
    raise ValueError(f"unknown literal type: {kind!r}")
