"""
Phase 2 - Syntax Analysis
Recursive-descent-equivalent LALR(1) grammar (built with PLY yacc) for the
C subset described in the project README. Builds an AST (see ast_nodes.py)
out of the token stream produced by Phase 1's lexer.
"""
import os

import ply.yacc as yacc

from phase2_syntax_analysis.ast_nodes import (
    ArrayAccess,
    ArrayDimension,
    Assignment,
    BinaryOp,
    CompoundStatement,
    Declaration,
    Declarator,
    DoWhileStatement,
    ExpressionStatement,
    ForStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IfStatement,
    InitializerList,
    InitDeclarator,
    JumpStatement,
    LabeledStatement,
    Literal,
    Parameter,
    Program,
    ReturnStatement,
    TypeSpecifier,
    UnaryOp,
    WhileStatement,
)
from phase1_lexical_analysis.lexer import build_lexer
from phase1_lexical_analysis.token_defs import tokens
from common.errors import add_syntax_error

# Operator precedence/associativity, including dangling-else resolution etc
precedence = (
    ("nonassoc", "IFX"),
    ("nonassoc", "ELSE"),
    ("right", "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MUL_ASSIGN", "DIV_ASSIGN", "MOD_ASSIGN"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQ", "NE"),
    ("left", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "MODULO"),
    ("right", "NOT", "UMINUS", "UPLUS", "ADDRESS", "PRE_INCREMENT", "PRE_DECREMENT"),
    ("left", "INCREMENT", "DECREMENT"),
)


def make_identifier(name, line):
    return Identifier(name, line)


def make_literal(token_type, value, line):
    return Literal(token_type, value, line)


def p_program(p):
    "program : external_declaration_list"
    p[0] = Program(p[1])


def p_external_declaration_list_recursive(p):
    "external_declaration_list : external_declaration_list external_declaration"
    p[0] = p[1] + [p[2]]


def p_external_declaration_list_single(p):
    "external_declaration_list : external_declaration"
    p[0] = [p[1]]


def p_external_declaration(p):
    """external_declaration : function_definition
                            | declaration
                            | typedef_declaration"""
    p[0] = p[1]


def p_function_definition(p):
    "function_definition : type_specifier function_declarator compound_statement"
    p[0] = FunctionDefinition(p[1], p[2], p[3], p[1].line)


# Record typedef names in the lexer so they can be recognized as TYPENAME later.
def p_typedef_declaration(p):
    "typedef_declaration : TYPEDEF type_specifier declarator_list SEMI"
    active_lexer = p.lexer  # the lexer instance this parse() call is using
    for declarator in p[3]:
        active_lexer.typedefs.add(declarator.name)
    init_declarators = [InitDeclarator(declarator, None, declarator.line) for declarator in p[3]]
    p[0] = Declaration(p[2], init_declarators, storage="typedef", line=p.lineno(1))


def p_declaration(p):
    "declaration : type_specifier init_declarator_list SEMI"
    p[0] = Declaration(p[1], p[2], line=p[1].line)


def p_type_specifier(p):
    """type_specifier : INT
                      | CHAR
                      | VOID
                      | TYPENAME"""
    p[0] = TypeSpecifier(str(p[1]), p.lineno(1))


def p_init_declarator_list_recursive(p):
    "init_declarator_list : init_declarator_list COMMA init_declarator"
    p[0] = p[1] + [p[3]]


def p_init_declarator_list_single(p):
    "init_declarator_list : init_declarator"
    p[0] = [p[1]]


def p_init_declarator_plain(p):
    "init_declarator : declarator"
    p[0] = InitDeclarator(p[1], None, p[1].line)


def p_init_declarator_initialized(p):
    "init_declarator : declarator ASSIGN initializer"
    p[0] = InitDeclarator(p[1], p[3], p[1].line)


def p_declarator_list_recursive(p):
    "declarator_list : declarator_list COMMA declarator"
    p[0] = p[1] + [p[3]]


def p_declarator_list_single(p):
    "declarator_list : declarator"
    p[0] = [p[1]]


def p_declarator_identifier(p):
    """declarator : IDENTIFIER
                  | function_declarator"""
    if isinstance(p[1], Declarator):
        p[0] = p[1]
        return
    p[0] = Declarator(p[1], line=p.lineno(1))


def p_declarator_array(p):
    "declarator : IDENTIFIER array_dimensions"
    p[0] = Declarator(p[1], kind_name="array", dimensions=p[2], line=p.lineno(1))


def p_function_declarator(p):
    "function_declarator : IDENTIFIER LPAREN parameter_list_opt RPAREN"
    p[0] = Declarator(p[1], kind_name="function", params=p[3], line=p.lineno(1))

# Support multi-dimensional arrays by accumulating one dimension at a time.
def p_array_dimensions_recursive(p):
    "array_dimensions : array_dimensions LBRACKET array_size_opt RBRACKET"
    p[0] = p[1] + [ArrayDimension(p[3], p.lineno(2))]


def p_array_dimensions_single(p):
    "array_dimensions : LBRACKET array_size_opt RBRACKET"
    p[0] = [ArrayDimension(p[2], p.lineno(1))]


def p_array_size_opt_expression(p):
    "array_size_opt : expression"
    p[0] = p[1]


def p_array_size_opt_empty(p):
    "array_size_opt : empty"
    p[0] = None


def p_parameter_list_opt(p):
    """parameter_list_opt : parameter_list
                          | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_parameter_list_recursive(p):
    "parameter_list : parameter_list COMMA parameter"
    p[0] = p[1] + [p[3]]


def p_parameter_list_single(p):
    "parameter_list : parameter"
    p[0] = [p[1]]


def p_parameter_identifier(p):
    "parameter : type_specifier IDENTIFIER"
    p[0] = Parameter(p[1], Declarator(p[2], line=p.lineno(2)), p.lineno(2))


def p_parameter_array(p):
    "parameter : type_specifier IDENTIFIER array_dimensions"
    p[0] = Parameter(p[1], Declarator(p[2], kind_name="array", dimensions=p[3], line=p.lineno(2)), p.lineno(2))


def p_statement(p):
    """statement : expression_statement
                 | compound_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
                 | labeled_statement
                 | declaration"""
    p[0] = p[1]


def p_compound_statement(p):
    "compound_statement : LBRACE block_item_list_opt RBRACE"
    p[0] = CompoundStatement(p[2], p.lineno(1))


def p_block_item_list_opt(p):
    """block_item_list_opt : block_item_list
                           | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_block_item_list_recursive(p):
    "block_item_list : block_item_list block_item"
    p[0] = p[1] + [p[2]]


def p_block_item_list_single(p):
    "block_item_list : block_item"
    p[0] = [p[1]]


def p_block_item(p):
    """block_item : statement"""
    p[0] = p[1]

# expression_opt allows standalone ';' to represent an empty statement.
def p_expression_statement(p):
    "expression_statement : expression_opt SEMI"
    p[0] = ExpressionStatement(p[1], p.lineno(2))

# gives unmatched if-statements lower precedence so ELSE binds to the nearest if.
def p_selection_statement_if(p):
    "selection_statement : IF LPAREN expression RPAREN statement %prec IFX"
    p[0] = IfStatement(p[3], p[5], None, p.lineno(1))


def p_selection_statement_if_else(p):
    "selection_statement : IF LPAREN expression RPAREN statement ELSE statement"
    p[0] = IfStatement(p[3], p[5], p[7], p.lineno(1))


def p_iteration_statement_while(p):
    "iteration_statement : WHILE LPAREN expression RPAREN statement"
    p[0] = WhileStatement(p[3], p[5], p.lineno(1))


def p_iteration_statement_do_while(p):
    "iteration_statement : DO statement WHILE LPAREN expression RPAREN SEMI"
    p[0] = DoWhileStatement(p[2], p[5], p.lineno(1))

# All three for-loop expressions are optional, allowing forms such as for (;;).
def p_iteration_statement_for(p):
    "iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement"
    p[0] = ForStatement(p[3], p[5], p[7], p[9], p.lineno(1))


def p_jump_statement_return(p):
    "jump_statement : RETURN expression_opt SEMI"
    p[0] = ReturnStatement(p[2], p.lineno(1))


def p_jump_statement_break(p):
    "jump_statement : BREAK SEMI"
    p[0] = JumpStatement("break", line=p.lineno(1))


def p_jump_statement_continue(p):
    "jump_statement : CONTINUE SEMI"
    p[0] = JumpStatement("continue", line=p.lineno(1))


def p_jump_statement_goto(p):
    "jump_statement : GOTO IDENTIFIER SEMI"
    p[0] = JumpStatement("goto", target=p[2], line=p.lineno(1))


def p_labeled_statement(p):
    "labeled_statement : IDENTIFIER COLON statement"
    p[0] = LabeledStatement(p[1], p[3], p.lineno(1))


def p_expression_opt(p):
    """expression_opt : expression
                      | empty"""
    p[0] = p[1]


def p_initializer_expression(p):
    "initializer : assignment_expression"
    p[0] = p[1]


def p_initializer_list(p):
    "initializer : LBRACE initializer_seq trailing_comma_opt RBRACE"
    p[0] = InitializerList(p[2], p.lineno(1))


def p_initializer_seq_recursive(p):
    "initializer_seq : initializer_seq COMMA initializer"
    p[0] = p[1] + [p[3]]


def p_initializer_seq_single(p):
    "initializer_seq : initializer"
    p[0] = [p[1]]


def p_trailing_comma_opt(p):
    """trailing_comma_opt : COMMA
                          | empty"""
    p[0] = None


def p_expression_comma(p):
    "expression : expression COMMA assignment_expression"
    p[0] = BinaryOp(",", p[1], p[3], p.lineno(2))


def p_expression_single(p):
    "expression : assignment_expression"
    p[0] = p[1]


def p_assignment_expression_assign(p):
    """assignment_expression : unary_expression ASSIGN assignment_expression
                             | unary_expression PLUS_ASSIGN assignment_expression
                             | unary_expression MINUS_ASSIGN assignment_expression
                             | unary_expression MUL_ASSIGN assignment_expression
                             | unary_expression DIV_ASSIGN assignment_expression
                             | unary_expression MOD_ASSIGN assignment_expression"""
    p[0] = Assignment(p[2], p[1], p[3], p.lineno(2))


def p_assignment_expression_logical(p):
    "assignment_expression : logical_or_expression"
    p[0] = p[1]


def p_logical_or_expression(p):
    """logical_or_expression : logical_or_expression OR logical_and_expression
                             | logical_and_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("||", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_logical_and_expression(p):
    """logical_and_expression : logical_and_expression AND equality_expression
                              | equality_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("&&", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_equality_expression(p):
    """equality_expression : equality_expression EQ relational_expression
                           | equality_expression NE relational_expression
                           | relational_expression"""
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_relational_expression(p):
    """relational_expression : relational_expression LT additive_expression
                             | relational_expression LE additive_expression
                             | relational_expression GT additive_expression
                             | relational_expression GE additive_expression
                             | additive_expression"""
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_additive_expression(p):
    """additive_expression : additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression
                           | multiplicative_expression"""
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_multiplicative_expression(p):
    """multiplicative_expression : multiplicative_expression MULTIPLY unary_expression
                                 | multiplicative_expression DIVIDE unary_expression
                                 | multiplicative_expression MODULO unary_expression
                                 | unary_expression"""
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]

# explicit precedence names distinguish prefix operators from their postfix forms.
def p_unary_expression_prefix(p):
    """unary_expression : INCREMENT unary_expression %prec PRE_INCREMENT
                        | DECREMENT unary_expression %prec PRE_DECREMENT
                        | NOT unary_expression
                        | MINUS unary_expression %prec UMINUS
                        | PLUS unary_expression %prec UPLUS
                        | ADDRESS unary_expression
                        | SIZEOF unary_expression"""
    p[0] = UnaryOp(p[1], p[2], "prefix", p.lineno(1))


def p_unary_expression_sizeof_type(p):
    "unary_expression : SIZEOF LPAREN type_specifier RPAREN"
    p[0] = UnaryOp("sizeof", p[3], "prefix", p.lineno(1))


def p_unary_expression_postfix(p):
    "unary_expression : postfix_expression"
    p[0] = p[1]


def p_postfix_expression_primary(p):
    "postfix_expression : primary_expression"
    p[0] = p[1]


def p_postfix_expression_array(p):
    "postfix_expression : postfix_expression LBRACKET expression RBRACKET"
    p[0] = ArrayAccess(p[1], p[3], p.lineno(2))


def p_postfix_expression_call(p):
    "postfix_expression : postfix_expression LPAREN argument_expression_list_opt RPAREN"
    p[0] = FunctionCall(p[1], p[3], p.lineno(2))


def p_postfix_expression_increment(p):
    "postfix_expression : postfix_expression INCREMENT"
    p[0] = UnaryOp("++", p[1], "postfix", p.lineno(2))


def p_postfix_expression_decrement(p):
    "postfix_expression : postfix_expression DECREMENT"
    p[0] = UnaryOp("--", p[1], "postfix", p.lineno(2))


def p_argument_expression_list_opt(p):
    """argument_expression_list_opt : argument_expression_list
                                    | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_argument_expression_list_recursive(p):
    "argument_expression_list : argument_expression_list COMMA assignment_expression"
    p[0] = p[1] + [p[3]]


def p_argument_expression_list_single(p):
    "argument_expression_list : assignment_expression"
    p[0] = [p[1]]


def p_primary_expression_identifier(p):
    "primary_expression : IDENTIFIER"
    p[0] = make_identifier(p[1], p.lineno(1))

# treat printf/scanf as ordinary identifier expressions so they can participate in calls.
def p_primary_expression_builtin_name(p):
    """primary_expression : PRINTF
                          | SCANF"""
    p[0] = make_identifier(str(p[1]), p.lineno(1))


def p_primary_expression_integer(p):
    "primary_expression : INTEGER_CONSTANT"
    p[0] = make_literal("int", p[1], p.lineno(1))


def p_primary_expression_char(p):
    "primary_expression : CHAR_CONSTANT"
    p[0] = make_literal("char", p[1], p.lineno(1))


def p_primary_expression_string(p):
    "primary_expression : STRING_LITERAL"
    p[0] = make_literal("string", p[1], p.lineno(1))


def p_primary_expression_grouped(p):
    "primary_expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_empty(p):
    "empty :"
    p[0] = None


def p_error(p):
    if p is None:
        add_syntax_error("Syntax Error: unexpected end of input")
        return

    add_syntax_error(f"Syntax Error: unexpected token '{p.value}' at line {p.lineno}")
    parser.errok()


_TABLE_DIR = os.path.dirname(os.path.abspath(__file__))

parser = yacc.yacc(
    start="program",
    tabmodule="parsetab",
    outputdir=_TABLE_DIR,
    debug=False,
    write_tables=True,
)


def parse_source(source_code: str):
    """Parses one complete source file using a brand-new lexer instance
    (see build_lexer()'s docstring for why this matters)."""
    fresh_lexer = build_lexer()
    fresh_lexer.lineno = 1
    return parser.parse(source_code, lexer=fresh_lexer)
