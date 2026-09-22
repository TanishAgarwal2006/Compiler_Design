"""
Phase 1 - Lexical Analysis
Reserved keywords and the master token list for the subset of C this
compiler supports
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

    # Floating-point and boolean base types
    "float": "FLOAT",
    "double": "DOUBLE",
    "bool": "BOOL",
    "_Bool": "BOOL",
    "true": "TRUE_KW",
    "false": "FALSE_KW",

    # Integer size / sign modifiers
    "short": "SHORT",
    "long": "LONG",
    "signed": "SIGNED",
    "unsigned": "UNSIGNED",

    # Qualifiers and storage classes
    "const": "CONST",
    "extern": "EXTERN",

    # C++ subset: classes, access control, free store
    "class": "CLASS",
    "public": "PUBLIC",
    "private": "PRIVATE",
    "protected": "PROTECTED",
    "new": "NEW",
    "delete": "DELETE",

    "return": "RETURN",
    "printf": "PRINTF",
    "scanf": "SCANF",
    "sizeof": "SIZEOF",
    "switch": "SWITCH",
    "case": "CASE",
    "default": "DEFAULT",
    "struct": "STRUCT",
    "union": "UNION",
    "enum": "ENUM",
    "static": "STATIC",
    "until": "UNTIL",
}

tokens = [
    "IDENTIFIER",
    "INTEGER_CONSTANT",
    "FLOAT_CONSTANT",
    "TYPENAME",
    "CHAR_CONSTANT",
    "STRING_LITERAL",

    # Scope resolution operator '::' (C++ subset)
    "SCOPE",

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
    "AND_ASSIGN",    # '&='
    "OR_ASSIGN",     # '|='
    "XOR_ASSIGN",    # '^='
    "LSHIFT_ASSIGN", # '<<='
    "RSHIFT_ASSIGN", # '>>='

    # Unary / pointer-adjacent operators
    "INCREMENT",
    "DECREMENT",
    "ADDRESS",  # '&' (address-of when unary, bitwise AND when binary)

    # Bitwise operators
    "BIT_OR",   # '|'
    "BIT_XOR",  # '^'
    "BIT_NOT",  # '~'
    "LSHIFT",   # '<<'
    "RSHIFT",   # '>>'

    # Relational & logical operators
    "EQ", "NE", "LE", "GE", "LT", "GT",
    "AND", "OR", "NOT", "ASSIGN",

    # Ternary conditional
    "QUESTION",

    # Variadic parameter marker
    "ELLIPSIS",  # '...'

    # Delimiters
    "SEMI", "COLON", "COMMA",
    "LPAREN", "RPAREN",
    "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET",

    # Struct/pointer member access
    "DOT",    # '.'  (struct member access)
    "ARROW",  # '->' (pointer member access)
]

# dict.fromkeys de-duplicates while preserving order: several spellings can map
# to the same token name (e.g. "bool" and "_Bool" both produce BOOL), and PLY
# warns about any token name listed twice.
tokens = tokens + list(dict.fromkeys(reserved.values()))