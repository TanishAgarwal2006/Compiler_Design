import ply.lex as lex
from utils.token import tokens, reserved
from utils.errors import add_lex_error

# Regular Expression Rules
# ----------------------------------------
# Note: PLY matches strings by length, so it safely matches '+=' before '+'
t_PLUS_ASSIGN  = r'\+='
t_MINUS_ASSIGN = r'-='
t_MUL_ASSIGN   = r'\*='
t_DIV_ASSIGN   = r'/='
t_MOD_ASSIGN   = r'%='

t_INCREMENT    = r'\+\+'
t_DECREMENT    = r'--'

t_PLUS         = r'\+'
t_MINUS        = r'-'
t_MULTIPLY     = r'\*'
t_DIVIDE       = r'/'
t_MODULO       = r'%'

t_EQ           = r'=='
t_NE           = r'!='
t_LE           = r'<='
t_GE           = r'>='
t_LT           = r'<'
t_GT           = r'>'
t_AND          = r'&&'
t_OR           = r'\|\|'
t_NOT          = r'!'
t_ASSIGN       = r'='
t_ADDRESS      = r'&'

t_SEMI         = r';'
t_COLON        = r':'
t_COMMA        = r','
t_LPAREN       = r'\('
t_RPAREN       = r'\)'
t_LBRACE       = r'\{'
t_RBRACE       = r'\}'
t_LBRACKET     = r'\['
t_RBRACKET     = r'\]'

# Complex Token Rules (Functions)
def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

def t_CHAR_CONSTANT(t):
    r'\'([^\\\n]|(\\.))\''
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Check if the identifier is a reserved keyword
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_INTEGER_CONSTANT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Track line numbers and ignored chars
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
    t.lexer.lineno += t.value.count('\n')

t_ignore = ' \t'

# Error Handling --> Stores list of all the errors encountered in the traversal
def t_error(t):
    add_lex_error(
        f"Lexical Error: Illegal character '{t.value[0]}' "
        f"at line {t.lexer.lineno}"
    )
# Build the lexer
lexer = lex.lex() 