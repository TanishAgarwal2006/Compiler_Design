"""
Phase 1 - Lexical Analysis

Converts raw C source text into a stream of tokens using PLY (Python Lex-Yacc).
Exclusive lexer states are used for block comments, string literals, and
character constants so that unterminated constructs are reported cleanly
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
t_INCREMENT = r"\+\+"
t_DECREMENT = r"--"
t_PLUS = r"\+"
t_MINUS = r"-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"/"
t_MODULO = r"%"
t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="
t_LT = r"<"
t_GT = r">"
t_AND = r"&&"
t_OR = r"\|\|"
t_NOT = r"!"
t_ASSIGN = r"="
t_ADDRESS = r"&"
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


def build_lexer():
    """Create an isolated lexer for one source input."""
    new_lexer = lex.lex()
    new_lexer.typedefs = set()
    return new_lexer


lexer = build_lexer()
