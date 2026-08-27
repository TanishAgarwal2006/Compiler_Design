"""
Phase 1 - Lexical Analysis
Reserved keywords and the master token list for the subset of C this
compiler supports (see the project README for the full feature list:
arithmetic/logical operators, if/else, for, while, do-while, integer and
char arrays, printf/scanf, function calls, goto/break/continue, recursive
functions, typedef, and multi-dimensional arrays).

NOTE: 'switch'/'case' are intentionally NOT part of this language subset -
they were never in the project specification, so the lexer does not
recognize them as keywords (they would lex as plain IDENTIFIER, which is
correct - not a bug).
"""

reserved = {
    "if": "IF",
    "else": "ELSE",
    "for": "FOR",
    "while": "WHILE",
    "do": "DO",
    "goto": "GOTO",
    "break": "BREAK",
    "continue": "CONTINUE",
    "typedef": "TYPEDEF",
    "int": "INT",
    "char": "CHAR",
    "void": "VOID",
    "return": "RETURN",
    "printf": "PRINTF",
    "scanf": "SCANF",
    "sizeof": "SIZEOF",
}

tokens = [
    "IDENTIFIER",
    "INTEGER_CONSTANT",
    "TYPENAME",
    "CHAR_CONSTANT",
    "STRING_LITERAL",

    # Arithmetic operators
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "DIVIDE",
    "MODULO",

    # Compound assignment operators
    "PLUS_ASSIGN",
    "MINUS_ASSIGN",
    "MUL_ASSIGN",
    "DIV_ASSIGN",
    "MOD_ASSIGN",

    # Unary / pointer-adjacent operators
    "INCREMENT",
    "DECREMENT",
    "ADDRESS",  # '&' (address-of, used for scanf arguments)

    # Relational & logical operators
    "EQ", "NE", "LE", "GE", "LT", "GT",
    "AND", "OR", "NOT", "ASSIGN",

    # Delimiters
    "SEMI", "COLON", "COMMA",
    "LPAREN", "RPAREN",
    "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET",
] + list(reserved.values())
