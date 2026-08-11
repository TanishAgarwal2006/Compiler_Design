# Reserved Keywords pertaining to our compiler 
# Includes project-required library functions printf and scanf,
# and sizeof support for arrays
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'do': 'DO',
    'goto': 'GOTO',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'typedef': 'TYPEDEF',
    'int': 'INT',
    'char': 'CHAR',
    'void': 'VOID',
    'return': 'RETURN',
    'printf': 'PRINTF',
    'scanf': 'SCANF',
    'sizeof': 'SIZEOF'  
}

# Token List
tokens = [
    'IDENTIFIER',        
    'INTEGER_CONSTANT',  
    'CHAR_CONSTANT',     
    'STRING_LITERAL',
    
    # Arithmetic & Specific Math Operators
    'PLUS',              
    'MINUS',             
    'MULTIPLY',         
    'DIVIDE',            
    'MODULO',            
    
    # Compound Assignments
    'PLUS_ASSIGN',
    'MINUS_ASSIGN',
    'MUL_ASSIGN',
    'DIV_ASSIGN',
    'MOD_ASSIGN',
    
    # Unary / Pointer / Address
    'INCREMENT',
    'DECREMENT',
    'ADDRESS',           # Represents '&'
    
    # Relational & Logical
    'EQ', 'NE', 'LE', 'GE', 'LT', 'GT',
    'AND', 'OR', 'NOT', 'ASSIGN',
    
    # Delimiters
    'SEMI', 'COLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET'
] + list(reserved.values())