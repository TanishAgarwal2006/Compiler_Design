import ply.lex as lex
from utils.token import tokens, reserved
from utils.errors import add_lex_error

# --------------------------- 0. State Setup ---------------------------
# exclusive states for constructs that span multiple characters or lines
states = (
    ('COMMENT', 'exclusive'),
    ('STRING', 'exclusive'),
    ('CHAR', 'exclusive'),
)

# Ignore spaces and tabs within these specific states
t_COMMENT_ignore = ' \t'
t_STRING_ignore = ''
t_CHAR_ignore = ''


# --------------------------- 1. Block & Line Comments ---------------------------
def t_begin_COMMENT(t):
    r'/\*'
    t.lexer.comment_start = t.lexer.lineno
    t.lexer.begin('COMMENT')

def t_COMMENT_end(t):
    r'\*/'
    t.lexer.begin('INITIAL')

def t_COMMENT_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT_eof(t):
    add_lex_error(f"Unterminated block comment starting at line {t.lexer.comment_start}")

def t_COMMENT_error(t):
    t.lexer.skip(1)

def t_LINE_COMMENT(t):
    r'//.*'
    pass


# --------------------------- 2. String Literals ---------------------------
def t_begin_STRING(t):
    r'\"'
    t.lexer.string_start = t.lexer.lineno
    t.lexer.string_buf = '"'
    t.lexer.begin('STRING')

# Capture any character inside the string, including escapes. 
def t_STRING_char(t):
    r'([^"\n\\]|\\.)+'
    t.lexer.string_buf += t.value

def t_STRING_end(t):
    r'\"'
    t.lexer.string_buf += '"'
    t.value = t.lexer.string_buf
    t.type = 'STRING_LITERAL'
    t.lexer.begin('INITIAL')
    return t

def t_STRING_newline(t):
    r'\n'
    add_lex_error(f"Unterminated string literal at line {t.lexer.string_start}")
    t.lexer.lineno += 1
    t.lexer.begin('INITIAL')

def t_STRING_eof(t):
    add_lex_error(f"Unterminated string literal at line {t.lexer.string_start}")

def t_STRING_error(t):
    t.lexer.string_buf += t.value[0]
    t.lexer.skip(1)


# --------------------------- 3. Character Constants ---------------------------
def t_begin_CHAR(t):
    r'\''
    t.lexer.char_start = t.lexer.lineno
    t.lexer.char_buf = "'"
    t.lexer.begin('CHAR')

# Capture any character inside the single quotes, including escapes.
def t_CHAR_content(t):
    r"([^'\\\n]|\\.)+"
    t.lexer.char_buf += t.value

def t_CHAR_end(t):
    r'\''
    t.lexer.char_buf += "'"
    
    # catch empty character literals ('') before they hit the parser
    if t.lexer.char_buf == "''":
        add_lex_error(f"Lexical Error: Empty character constant at line {t.lexer.char_start}")
        t.lexer.begin('INITIAL')
        # We do not return 't' here, effectively dropping the malformed token
        return 
        
    t.value = t.lexer.char_buf
    t.type = 'CHAR_CONSTANT'
    t.lexer.begin('INITIAL')
    return t

def t_CHAR_newline(t):
    r'\n'
    add_lex_error(f"Lexical Error: Unterminated character constant at line {t.lexer.char_start}")
    t.lexer.lineno += 1
    t.lexer.begin('INITIAL') # drop token due to error

def t_CHAR_eof(t):
    add_lex_error(f"Lexical Error: Unterminated character constant at EOF (started at line {t.lexer.char_start})")
    t.lexer.begin('INITIAL')

def t_CHAR_error(t):
    t.lexer.char_buf += t.value[0]
    t.lexer.skip(1)
    

# --------------------------- 4. Complex Tokens (Numbers & Identifiers) ---------------------------
# Note: Base-specific integer rules must precede the decimal rule 
# so prefixes like '0x' or '0b' are matched first.

def t_INTEGER_HEX(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    t.type = 'INTEGER_CONSTANT'
    return t

def t_INTEGER_BIN(t):
    r'0[bB][01]+'
    t.value = int(t.value, 2)
    t.type = 'INTEGER_CONSTANT'
    return t

def t_INTEGER_OCT(t):
    r'0[0-7]+'
    t.value = int(t.value, 8)
    t.type = 'INTEGER_CONSTANT'
    return t

# executes before t_INTEGER_DEC to catch malformed octals (e.g., 09) 
# instead of silently splitting them into '0' and '9'
def t_INVALID_OCTAL(t):
    r'0[0-7]*[89][0-9]*'
    add_lex_error(f"Invalid octal literal '{t.value}' at line {t.lexer.lineno}")
    t.lexer.skip(len(t.value))

def t_INTEGER_DEC(t):
    r'([1-9]\d*|0)'
    t.value = int(t.value, 10)
    t.type = 'INTEGER_CONSTANT'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    t.type = reserved.get(t.value, 'IDENTIFIER')
    
    # Lexer Hack: If the parser previously registered this identifier 
    # as a typedef, dynamically swap its token type to TYPENAME.
    # will be helpful in the parsing stage
    if t.type == 'IDENTIFIER':
        if hasattr(t.lexer, 'typedefs') and t.value in t.lexer.typedefs:
            t.type = 'TYPENAME'
            
    return t


# --------------------------- 5. Standard Operators & Delimiters ---------------------------
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


# --------------------------- 6. Global Rules & Error Handling ---------------------------
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore global spaces and tabs in INITIAL state
t_ignore = ' \t'

def t_error(t):
    add_lex_error(f"Lexical Error: Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Initialize the Lexer instance
lexer = lex.lex()