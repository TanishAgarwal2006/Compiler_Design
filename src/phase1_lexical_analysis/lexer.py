"""
Phase 1 - Lexical Analysis

Converts raw C source text into a stream of tokens using PLY
Lexer states used for - comments, strings, characters, so that unterminated constructs are reported cleanly
instead of desynchronizing the rest of the token stream.
"""
import ply.lex as lex

from phase1_lexical_analysis.token_defs import tokens, reserved
from common.errors import add_lex_error

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
    add_lex_error(f"Unterminated block comment starting at line {t.lexer.comment_start}")


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


_VALID_ESCAPES = set("nrtbfv0\\'\"a")


def t_CHAR_end(t):
    r"\'"
    t.lexer.char_buf += "'"
    inner = t.lexer.char_buf[1:-1]

    if inner == "":
        add_lex_error(f"Lexical Error: Empty character constant at line {t.lexer.char_start}")
        t.lexer.begin("INITIAL")
        return  # malformed token is dropped, not returned to the parser

    if inner.startswith("\\"):
        if len(inner) != 2 or inner[1] not in _VALID_ESCAPES:
            add_lex_error(
                f"Lexical Error: Invalid escape sequence '{inner}' in character "
                f"constant at line {t.lexer.char_start}"
            )
            t.lexer.begin("INITIAL")
            return
    elif len(inner) != 1:
        add_lex_error(
            f"Lexical Error: Multi-character constant {t.lexer.char_buf} at "
            f"line {t.lexer.char_start} (only single characters are allowed)"
        )
        t.lexer.begin("INITIAL")
        return

    t.value = t.lexer.char_buf
    t.type = "CHAR_CONSTANT"
    t.lexer.begin("INITIAL")
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


def t_FLOAT_CONSTANT(t):
    r"(?:\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)[fFlL]?"
    text = t.value
    suffix = ""
    if text[-1] in "fFlL":
        suffix = text[-1]
        text = text[:-1]
    t.value = float(text)
    t.float_suffix = suffix
    return t


# Base-specific integer rules precede the decimal rule.

def t_INTEGER_HEX(t):
    r"0[xX][0-9a-fA-F]+"
    t.value = int(t.value, 16)
    t.type = "INTEGER_CONSTANT"
    return t


def t_INTEGER_BIN(t):
    r"0[bB][01]+"
    t.value = int(t.value, 2)
    t.type = "INTEGER_CONSTANT"
    return t


def t_INTEGER_OCT(t):
    r"0[0-7]+"
    t.value = int(t.value, 8)
    t.type = "INTEGER_CONSTANT"
    return t


def t_INVALID_OCTAL(t):
    r"0[0-7]*[89][0-9]*"
    add_lex_error(f"Lexical Error: Invalid octal literal '{t.value}' at line {t.lexer.lineno}")
    t.lexer.skip(len(t.value))


def t_INTEGER_DEC(t):
    r"([1-9]\d*|0)"
    t.value = int(t.value, 10)
    t.type = "INTEGER_CONSTANT"
    return t


def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")

    if t.type == "IDENTIFIER" and hasattr(t.lexer, "typedefs") and t.value in t.lexer.typedefs:
        t.type = "TYPENAME"

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
    new_lexer.directives = []
    return new_lexer


lexer = build_lexer()