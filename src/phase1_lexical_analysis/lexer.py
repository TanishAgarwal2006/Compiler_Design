"""
Phase 1 - Lexical Analysis

Converts raw C source text into a stream of tokens using PLY
Lexer states used for - comments, strings, characters, so that unterminated constructs are reported cleanly
instead of desynchronizing the rest of the token stream.
"""
import re

import ply.lex as lex

from phase1_lexical_analysis.token_defs import tokens, reserved
from common.errors import add_lex_error
from common.literals import ESCAPE, bad_escapes

# States for constructs that span multiple characters or lines.
states = (
    ("COMMENT", "exclusive"),
    ("STRING", "exclusive"),
    ("CHAR", "exclusive"),
)

t_COMMENT_ignore = " \t"
t_STRING_ignore = ""
t_CHAR_ignore = ""


def t_begin_COMMENT(t):
    r"/\*"
    t.lexer.comment_start = t.lexer.lineno
    t.lexer.begin("COMMENT")


def t_COMMENT_end(t):
    r"\*/"
    t.lexer.begin("INITIAL")


def t_COMMENT_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_COMMENT_eof(t):
    add_lex_error(f"Unterminated block comment at line {t.lexer.comment_start}")


def t_COMMENT_error(t):
    t.lexer.skip(1)


def t_LINE_COMMENT(t):
    r"//.*"
    pass


def t_begin_STRING(t):
    r"\""
    t.lexer.string_start = t.lexer.lineno
    t.lexer.string_buf = '"'
    t.lexer.begin("STRING")


def t_STRING_char(t):
    r'([^"\n\\]|\\.)+'
    t.lexer.string_buf += t.value


def t_STRING_end(t):
    r"\""
    t.lexer.string_buf += '"'
    for bad in bad_escapes(t.lexer.string_buf[1:-1]):
        add_lex_error(f"Lexical Error: Invalid escape sequence '{bad}' in string literal at line {t.lexer.string_start}")
    t.value = t.lexer.string_buf
    t.type = "STRING_LITERAL"
    t.lexer.begin("INITIAL")
    return t


def t_STRING_newline(t):
    r"\n"
    add_lex_error(f"Lexical Error: Unterminated string literal at line {t.lexer.string_start}")
    t.lexer.lineno += 1
    t.lexer.begin("INITIAL")


def t_STRING_eof(t):
    add_lex_error(f"Lexical Error: Unterminated string literal at line {t.lexer.string_start}")


def t_STRING_error(t):
    t.lexer.string_buf += t.value[0]
    t.lexer.skip(1)


def t_begin_CHAR(t):
    r"\'"
    t.lexer.char_start = t.lexer.lineno
    t.lexer.char_buf = "'"
    t.lexer.begin("CHAR")


def t_CHAR_content(t):
    r"([^'\\\n]|\\.)+"
    t.lexer.char_buf += t.value


def t_CHAR_end(t):
    r"\'"
    t.lexer.char_buf += "'"
    inner = t.lexer.char_buf[1:-1]
    line = t.lexer.char_start
    t.lexer.begin("INITIAL")

    if inner == "":
        add_lex_error(f"Lexical Error: Empty character constant at line {line}")
        return  # malformed token is dropped, not returned to the parser

    if inner.startswith("\\"):
        if not ESCAPE.fullmatch(inner):
            bad = bad_escapes(inner)
            if bad:
                add_lex_error(f"Lexical Error: Invalid escape sequence '{bad[0]}' in character constant at line {line}")
            else:
                add_lex_error(f"Lexical Error: Multi-character constant {t.lexer.char_buf} (only single characters are allowed) at line {line}")
            return
    elif len(inner) != 1:
        add_lex_error(f"Lexical Error: Multi-character constant {t.lexer.char_buf} (only single characters are allowed) at line {line}")
        return
    elif ord(inner) > 127:
        add_lex_error(f"Lexical Error: Non-ASCII character {t.lexer.char_buf} in character constant at line {line}")
        return

    t.value = t.lexer.char_buf
    t.type = "CHAR_CONSTANT"
    return t


def t_CHAR_newline(t):
    r"\n"
    add_lex_error(f"Lexical Error: Unterminated character constant at line {t.lexer.char_start}")
    t.lexer.lineno += 1
    t.lexer.begin("INITIAL")


def t_CHAR_eof(t):
    add_lex_error(f"Lexical Error: Unterminated character constant at EOF (started at line {t.lexer.char_start})")
    t.lexer.begin("INITIAL")


def t_CHAR_error(t):
    t.lexer.char_buf += t.value[0]
    t.lexer.skip(1)


# ---------------------------------------------------------------------------
# Preprocessor directives
#
# This compiler has no preprocessor pass, but real C sources always open with
# "#include <stdio.h>". Rather than choking on '#' as an illegal character,
# Phase 1 recognises a directive, records it on the lexer for reporting, and
# consumes the whole line so the token stream stays clean. Unknown directives
# are still reported as lexical errors.
# ---------------------------------------------------------------------------
_KNOWN_DIRECTIVES = {
    "include", "define", "undef", "ifdef", "ifndef", "if", "else",
    "elif", "endif", "pragma", "line", "error", "warning",
}


def t_PREPROCESSOR(t):
    r"\#[ \t]*[A-Za-z_][A-Za-z_0-9]*[^\n]*"
    body = t.value[1:].strip()
    name = body.split()[0] if body.split() else ""
    if name not in _KNOWN_DIRECTIVES:
        add_lex_error(f"Lexical Error: Unknown preprocessor directive '#{name}' at line {t.lexer.lineno}")
        return
    if not hasattr(t.lexer, "directives"):
        t.lexer.directives = []
    t.lexer.directives.append((t.lexer.lineno, "#" + body))
    # directive consumed; no token reaches the parser


def t_STRAY_HASH(t):
    r"\#"
    add_lex_error(f"Lexical Error: Stray '#' at line {t.lexer.lineno}")


# ---------------------------------------------------------------------------
# Numeric literals
#
# Floating-point rules are declared before the integer rules so that "3.14"
# and "2e10" are never split into an integer, a dot and another integer.
# ---------------------------------------------------------------------------

def t_INVALID_FLOAT(t):
    r"(?:\d+\.\d*|\.\d+)(?:\.[0-9.]*)|(?:\d+\.?\d*|\.\d+)[eE][+-]?(?![0-9+\-])"
    add_lex_error(f"Lexical Error: Malformed floating-point literal '{t.value}' at line {t.lexer.lineno}")


# Integer suffixes (u, l, ul, ll, ull in any case/order) are accepted and dropped:
# "long" and "unsigned" are plain int in this compiler. A number glued to
# letters that are not a valid suffix ("45abc", "0x1G") is one lexical error,
# not a number followed by an identifier. (?![A-Za-z0-9_]) enforces that.
_INT_SUFFIX = r"(?:[uU](?:ll|LL|[lL])?|(?:ll|LL|[lL])[uU]?)?(?![A-Za-z0-9_])"
_NUMBER_END = r"(?![A-Za-z0-9_])"


@lex.TOKEN(r"(?:\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)[fFlL]?" + _NUMBER_END)
def t_FLOAT_CONSTANT(t):
    text = t.value
    suffix = ""
    if text[-1] in "fFlL":
        suffix = text[-1]
        text = text[:-1]
    t.value = float(text)
    t.float_suffix = suffix
    return t


def _strip_suffix(text):
    return text.rstrip("uUlL")


# Base-specific integer rules precede the decimal rule.

@lex.TOKEN(r"0[xX][0-9a-fA-F]+" + _INT_SUFFIX)
def t_INTEGER_HEX(t):
    t.value = int(_strip_suffix(t.value), 16)
    t.type = "INTEGER_CONSTANT"
    return t


@lex.TOKEN(r"0[bB][01]+" + _INT_SUFFIX)
def t_INTEGER_BIN(t):
    t.value = int(_strip_suffix(t.value), 2)
    t.type = "INTEGER_CONSTANT"
    return t


@lex.TOKEN(r"0[0-7]+" + _INT_SUFFIX)
def t_INTEGER_OCT(t):
    t.value = int(_strip_suffix(t.value), 8)
    t.type = "INTEGER_CONSTANT"
    return t


def t_INVALID_OCTAL(t):
    r"0[0-7]*[89][0-9]*"
    add_lex_error(f"Lexical Error: Invalid octal literal '{t.value}' at line {t.lexer.lineno}")


@lex.TOKEN(r"([1-9]\d*|0)" + _INT_SUFFIX)
def t_INTEGER_DEC(t):
    t.value = int(_strip_suffix(t.value), 10)
    t.type = "INTEGER_CONSTANT"
    return t


def t_INVALID_NUMBER(t):
    r"(?:0[xX][0-9a-fA-F]*|0[bB][01]*|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)[A-Za-z_0-9]+"
    v = t.value
    if v[:2] in ("0x", "0X"):
        what = "hex literal (digits 0-9 and a-f only, at least one needed)"
    elif v[:2] in ("0b", "0B"):
        what = "binary literal (digits 0 and 1 only, at least one needed)"
    else:
        what = "number (letters directly after digits are only allowed as the suffixes u, l, ul, ll, f)"
    add_lex_error(f"Lexical Error: Invalid {what}: '{v}' at line {t.lexer.lineno}")


# A class name directly followed by '(' (but not "(*", a function-pointer
# declarator) is a constructor/destructor name, e.g. "Dog(int n)" or "~Dog()".
# The grammar cannot tell it from a type name without looking one token ahead,
# so the lexer does that look-ahead, the same way it already tells TYPENAME
# from IDENTIFIER.
_CTOR_AHEAD = re.compile(r"\s*\((?!\s*\*)")


def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")

    if t.type == "IDENTIFIER" and hasattr(t.lexer, "typedefs") and t.value in t.lexer.typedefs:
        t.type = "TYPENAME"
        if t.value in t.lexer.class_names and _CTOR_AHEAD.match(t.lexer.lexdata, t.lexer.lexpos):
            t.type = "CTOR_NAME"

    return t


t_PLUS_ASSIGN = r"\+="
t_MINUS_ASSIGN = r"-="
t_MUL_ASSIGN = r"\*="
t_DIV_ASSIGN = r"/="
t_MOD_ASSIGN = r"%="
t_AND_ASSIGN = r"&="
t_OR_ASSIGN = r"\|="
t_XOR_ASSIGN = r"\^="
t_LSHIFT_ASSIGN = r"<<="
t_RSHIFT_ASSIGN = r">>="
t_INCREMENT = r"\+\+"
t_DECREMENT = r"--"
t_ELLIPSIS = r"\.\.\."  # must be tried before t_DOT ('.')
t_SCOPE = r"::"  # C++ scope resolution; must be tried before t_COLON (':')
t_ARROW = r"->"  # must be tried before MINUS ('-') and t_DOT ('.')
t_DOT = r"\."
t_PLUS = r"\+"
t_MINUS = r"-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"
t_MODULO = r"%"
t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="
t_LSHIFT = r"<<"  # must be tried before t_LT ('<')
t_RSHIFT = r">>"  # must be tried before t_GT ('>')
t_LT = r"<"
t_GT = r">"
t_AND = r"&&"
t_OR = r"\|\|"
t_BIT_OR = r"\|"
t_BIT_XOR = r"\^"
t_BIT_NOT = r"~"
t_NOT = r"!"
t_ASSIGN = r"="
t_ADDRESS = r"&"
t_QUESTION = r"\?"
t_SEMI = r";"
t_COLON = r":"
t_COMMA = r","
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t"


def t_error(t):
    add_lex_error(f"Lexical Error: Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


# Predefined typenames available without an explicit typedef, mirroring the
# handful of library types a <stdio.h>-free toy compiler still needs to
# recognize (e.g. "FILE *fp = fopen(...)" for file manipulation).
_BUILTIN_TYPEDEFS = {"FILE", "size_t", "ptrdiff_t", "va_list"}


def build_lexer():
    """Create an isolated lexer for one source input."""
    new_lexer = lex.lex()
    new_lexer.typedefs = set(_BUILTIN_TYPEDEFS)
    new_lexer.class_names = set()   # names introduced by 'class X' (the parser fills this in)
    new_lexer.directives = []
    return new_lexer


lexer = build_lexer()