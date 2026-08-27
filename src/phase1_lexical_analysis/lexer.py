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

# --------------------------- 0. State Setup ---------------------------
# Exclusive states for constructs that span multiple characters or lines.
states = (
    ("COMMENT", "exclusive"),
    ("STRING", "exclusive"),
    ("CHAR", "exclusive"),
)

t_COMMENT_ignore = " \t"
t_STRING_ignore = ""
t_CHAR_ignore = ""


# --------------------------- 1. Block & Line Comments ---------------------------
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


# --------------------------- 2. String Literals ---------------------------
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


# --------------------------- 3. Character Constants ---------------------------
def t_begin_CHAR(t):
    r"\'"
    t.lexer.char_start = t.lexer.lineno
    t.lexer.char_buf = "'"
    t.lexer.begin("CHAR")


def t_CHAR_content(t):
    r"([^'\\\n]|\\.)+"
    t.lexer.char_buf += t.value


# Recognized single-character C escape sequences. Kept as a set so the
# validity check below doubles as documentation of what's supported.
_VALID_ESCAPES = set("nrtbfv0\\'\"a")


def t_CHAR_end(t):
    r"\'"
    t.lexer.char_buf += "'"
    inner = t.lexer.char_buf[1:-1]  # content between the quotes

    if inner == "":
        add_lex_error(f"Lexical Error: Empty character constant at line {t.lexer.char_start}")
        t.lexer.begin("INITIAL")
        return  # malformed token is dropped, not returned to the parser

    if inner.startswith("\\"):
        # A valid escape is exactly backslash + one character, e.g. '\n', '\''.
        if len(inner) != 2 or inner[1] not in _VALID_ESCAPES:
            add_lex_error(
                f"Lexical Error: Invalid escape sequence '{inner}' in character "
                f"constant at line {t.lexer.char_start}"
            )
            t.lexer.begin("INITIAL")
            return
    elif len(inner) != 1:
        # Multi-character constants like 'AB' are not part of this language
        # subset (they are a non-portable GCC extension in real C).
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


# --------------------------- 4. Numbers & Identifiers ---------------------------
# Base-specific integer rules must precede the plain decimal rule so that
# prefixes like '0x' or '0b' are matched first.

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

    # Lexer/parser feedback loop: once the parser has reduced a
    # 'typedef ... NAME;' declaration it registers NAME in lexer.typedefs,
    # so any later occurrence of that identifier is retyped as TYPENAME.
    # This is the standard "lexer hack" required to parse C-style typedefs
    # with a context-free grammar.
    if t.type == "IDENTIFIER" and hasattr(t.lexer, "typedefs") and t.value in t.lexer.typedefs:
        t.type = "TYPENAME"

    return t


# --------------------------- 5. Operators & Delimiters ---------------------------
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


# --------------------------- 6. Global Rules & Error Handling ---------------------------
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t"


def t_error(t):
    add_lex_error(f"Lexical Error: Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


def build_lexer():
    """
    Factory that returns a brand-new, independent lexer instance.

    IMPORTANT: always prefer this over reusing a single shared lexer across
    multiple source files in the same process. PLY's lexer.input() does
    NOT reset lexstate (the current exclusive state) or any of the
    lexer.* attributes set above (comment_start, string_buf, typedefs,
    ...). If one file leaves the lexer mid-COMMENT/STRING/CHAR state (e.g.
    an "unterminated comment" test case) and the *same* lexer object is
    then reused for the next file, the next file's tokens get silently
    swallowed as if they were still inside that comment. build_lexer()
    sidesteps the whole bug class by never sharing lexer state between
    inputs; parse_source() and the test harness both rely on this.
    """
    new_lexer = lex.lex()
    new_lexer.typedefs = set()
    return new_lexer


# Module-level convenience instance for simple one-off, single-file use
# (e.g. an interactive shell). Anything that processes more than one file
# per process - the test harness, batch tools - should call build_lexer()
# instead.
lexer = build_lexer()
