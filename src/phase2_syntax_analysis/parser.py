"""
Phase 2 - Syntax Analysis
Recursive-descent-equivalent LALR(1) grammar (built with PLY yacc) for the
C subset described in the project README. Builds an AST (see ast_nodes.py)
out of the token stream produced by Phase 1's lexer.
"""
import os

import ply.yacc as yacc

from phase2_syntax_analysis.ast_nodes import (
    AccessLabel,
    ArrayAccess,
    ArrayDimension,
    Assignment,
    BinaryOp,
    BaseSpecifier,
    CastExpression,
    ClassSpecifier,
    CompoundStatement,
    ConditionalExpression,
    Declaration,
    Declarator,
    DeleteExpression,
    DoUntilStatement,
    DoWhileStatement,
    EnumSpecifier,
    Enumerator,
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
    MemberAccess,
    NewExpression,
    Parameter,
    Program,
    QualifiedName,
    ReturnStatement,
    StructSpecifier,
    SwitchCase,
    SwitchStatement,
    TypeSpecifier,
    UnaryOp,
    UntilStatement,
    VarArgsParameter,
    WhileStatement,
)
from phase1_lexical_analysis.lexer import build_lexer
from phase1_lexical_analysis.token_defs import tokens
from common.errors import add_syntax_error

# Operator precedence/associativity, including dangling-else resolution etc
precedence = (
    ("nonassoc", "IFX"),
    ("nonassoc", "ELSE"),
    ("right", "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MUL_ASSIGN", "DIV_ASSIGN", "MOD_ASSIGN",
     "AND_ASSIGN", "OR_ASSIGN", "XOR_ASSIGN", "LSHIFT_ASSIGN", "RSHIFT_ASSIGN"),
    ("right", "QUESTION", "COLON"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "BIT_OR"),
    ("left", "BIT_XOR"),
    ("left", "ADDRESS"),  # binary '&' (bitwise AND) shares its token with unary address-of
    ("left", "EQ", "NE"),
    ("left", "LT", "LE", "GT", "GE"),
    ("left", "LSHIFT", "RSHIFT"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "MODULO"),
    ("right", "NOT", "BIT_NOT", "UMINUS", "UPLUS", "DEREF", "PRE_INCREMENT", "PRE_DECREMENT", "CAST",
     "NEW", "DELETE"),
    ("left", "INCREMENT", "DECREMENT", "DOT", "ARROW"),
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
    # external_declaration is None only for a recovered "error SEMI" - drop it
    # rather than adding a hole to the declaration list.
    p[0] = p[1] if p[2] is None else p[1] + [p[2]]


def p_external_declaration_list_single(p):
    "external_declaration_list : external_declaration"
    p[0] = [] if p[1] is None else [p[1]]


def p_external_declaration(p):
    """external_declaration : function_definition
                            | declaration
                            | typedef_declaration"""
    p[0] = p[1]


# Same panic-mode recovery as p_statement_error, for a malformed
# declaration/definition at file scope (outside any function body).
def p_external_declaration_error(p):
    "external_declaration : error SEMI"
    p[0] = None
    parser.errok()


def p_function_definition(p):
    "function_definition : type_specifier function_declarator compound_statement"
    p[0] = FunctionDefinition(p[1], p[2], p[3], storage=None, line=p[1].line)


def p_function_definition_storage(p):
    "function_definition : storage_class type_specifier function_declarator compound_statement"
    p[0] = FunctionDefinition(p[2], p[3], p[4], storage=p[1], line=p[2].line)


# "static" and "extern" behave identically as far as the grammar is concerned;
# a single nonterminal keeps the declaration/definition rules from doubling.
def p_storage_class(p):
    """storage_class : STATIC
                     | EXTERN"""
    p[0] = str(p[1])


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


def p_declaration_storage(p):
    "declaration : storage_class type_specifier init_declarator_list SEMI"
    p[0] = Declaration(p[2], p[3], storage=p[1], line=p[2].line)


# C spells a single type with several keywords ("unsigned long int"), so the
# base type is collected as a sequence and joined back into one TypeSpecifier
# name. Declaring it as a left-recursive list keeps the grammar LALR(1): after
# each keyword the parser either shifts another type keyword or reduces.
def p_type_specifier_builtin(p):
    "type_specifier : builtin_type_seq"
    names, line = p[1]
    p[0] = TypeSpecifier(" ".join(names), line)


def p_type_specifier_typename(p):
    "type_specifier : TYPENAME"
    p[0] = TypeSpecifier(str(p[1]), p.lineno(1))


def p_builtin_type_seq_recursive(p):
    "builtin_type_seq : builtin_type_seq builtin_type"
    names, line = p[1]
    p[0] = (names + [p[2]], line)


def p_builtin_type_seq_single(p):
    "builtin_type_seq : builtin_type"
    p[0] = ([p[1]], p.lineno(1))


def p_builtin_type(p):
    """builtin_type : INT
                    | CHAR
                    | VOID
                    | FLOAT
                    | DOUBLE
                    | BOOL
                    | SHORT
                    | LONG
                    | SIGNED
                    | UNSIGNED"""
    p[0] = str(p[1])


# "const int x" - the qualifier is folded into the type name so that every
# later phase sees one TypeSpecifier instead of a separate qualifier node.
def p_type_specifier_const(p):
    "type_specifier : CONST type_specifier"
    inner = p[2]
    if isinstance(inner, TypeSpecifier):
        p[0] = TypeSpecifier("const " + inner.name, p.lineno(1))
    else:
        inner.is_const = True
        p[0] = inner


def p_type_specifier_struct(p):
    "type_specifier : struct_specifier"
    p[0] = p[1]


def p_type_specifier_enum(p):
    "type_specifier : enum_specifier"
    p[0] = p[1]


def p_type_specifier_class(p):
    "type_specifier : class_specifier"
    p[0] = p[1]


# struct/union share the same shape; is_union distinguishes them on the AST node.
def p_struct_specifier_defined(p):
    """struct_specifier : STRUCT IDENTIFIER LBRACE member_declaration_list RBRACE
                        | UNION IDENTIFIER LBRACE member_declaration_list RBRACE"""
    p[0] = StructSpecifier(p[2], p[4], is_union=(str(p[1]) == "union"), line=p.lineno(1))


def p_struct_specifier_anonymous(p):
    """struct_specifier : STRUCT LBRACE member_declaration_list RBRACE
                        | UNION LBRACE member_declaration_list RBRACE"""
    p[0] = StructSpecifier(None, p[3], is_union=(str(p[1]) == "union"), line=p.lineno(1))


# a bare "struct Point" reference (variable declaration or forward reference).
def p_struct_specifier_reference(p):
    """struct_specifier : STRUCT IDENTIFIER
                        | UNION IDENTIFIER"""
    p[0] = StructSpecifier(p[2], None, is_union=(str(p[1]) == "union"), line=p.lineno(1))


# One member list serves struct, union and class. A member is an ordinary
# declaration, an inline member-function definition, or an access label
# ("public:") that applies to every member that follows it.
def p_member_declaration_list_recursive(p):
    "member_declaration_list : member_declaration_list member_declaration"
    p[0] = p[1] + [p[2]]


def p_member_declaration_list_single(p):
    "member_declaration_list : member_declaration"
    p[0] = [p[1]]


def p_member_declaration(p):
    """member_declaration : declaration
                          | function_definition
                          | typedef_declaration"""
    p[0] = p[1]


def p_member_declaration_access(p):
    "member_declaration : access_specifier COLON"
    p[0] = AccessLabel(p[1], p.lineno(2))


def p_access_specifier(p):
    """access_specifier : PUBLIC
                        | PRIVATE
                        | PROTECTED"""
    p[0] = str(p[1])


# ---------------------------------------------------------------------------
# Classes (C++ subset): optional base list, access labels, inline methods.
# ---------------------------------------------------------------------------
# "class_head" is reduced as soon as the class name has been read, before the
# body is parsed. That matters because the name is registered with the lexer
# there, so a member such as "Node *next;" inside the body already sees the
# class name as a TYPENAME. Every alternative below is non-empty, which keeps
# the head/reference/body forms free of reduce-reduce conflicts.
def p_class_head(p):
    "class_head : CLASS IDENTIFIER"
    p.lexer.typedefs.add(p[2])
    p[0] = (p[2], p.lineno(1))


def p_class_specifier_plain_body(p):
    "class_specifier : class_head LBRACE member_declaration_list RBRACE"
    name, line = p[1]
    p[0] = ClassSpecifier(name, [], p[3], line=line)


def p_class_specifier_plain_empty(p):
    "class_specifier : class_head LBRACE RBRACE"
    name, line = p[1]
    p[0] = ClassSpecifier(name, [], [], line=line)


def p_class_specifier_derived_body(p):
    "class_specifier : class_head COLON base_specifier_list LBRACE member_declaration_list RBRACE"
    name, line = p[1]
    p[0] = ClassSpecifier(name, p[3], p[5], line=line)


def p_class_specifier_derived_empty(p):
    "class_specifier : class_head COLON base_specifier_list LBRACE RBRACE"
    name, line = p[1]
    p[0] = ClassSpecifier(name, p[3], [], line=line)


# a bare "class Node;" forward reference or "class Node n;" use.
def p_class_specifier_reference(p):
    "class_specifier : class_head"
    name, line = p[1]
    p[0] = ClassSpecifier(name, [], None, line=line)


def p_base_specifier_list_recursive(p):
    "base_specifier_list : base_specifier_list COMMA base_specifier"
    p[0] = p[1] + [p[3]]


def p_base_specifier_list_single(p):
    "base_specifier_list : base_specifier"
    p[0] = [p[1]]


# "class Dog : public Animal" - the access keyword is optional, matching C++.
def p_base_specifier_qualified(p):
    "base_specifier : access_specifier class_name"
    p[0] = BaseSpecifier(p[2], p[1], p.lineno(1))


def p_base_specifier_plain(p):
    "base_specifier : class_name"
    p[0] = BaseSpecifier(p[1], "private", p.lineno(1))


# A base class may already be a known TYPENAME (registered by typedef) or a
# plain IDENTIFIER that was introduced by an earlier "class" definition.
def p_class_name(p):
    """class_name : IDENTIFIER
                  | TYPENAME"""
    p[0] = str(p[1])


def p_enum_specifier_defined(p):
    "enum_specifier : ENUM IDENTIFIER LBRACE enumerator_list RBRACE"
    p[0] = EnumSpecifier(p[2], p[4], p.lineno(1))


def p_enum_specifier_anonymous(p):
    "enum_specifier : ENUM LBRACE enumerator_list RBRACE"
    p[0] = EnumSpecifier(None, p[3], p.lineno(1))


def p_enum_specifier_reference(p):
    "enum_specifier : ENUM IDENTIFIER"
    p[0] = EnumSpecifier(p[2], None, p.lineno(1))


def p_enumerator_list_recursive(p):
    "enumerator_list : enumerator_list COMMA enumerator"
    p[0] = p[1] + [p[3]]


def p_enumerator_list_single(p):
    "enumerator_list : enumerator"
    p[0] = [p[1]]


def p_enumerator_plain(p):
    "enumerator : IDENTIFIER"
    p[0] = Enumerator(p[1], None, p.lineno(1))


def p_enumerator_valued(p):
    "enumerator : IDENTIFIER ASSIGN assignment_expression"
    p[0] = Enumerator(p[1], p[3], p.lineno(1))


# allow a trailing comma after the last enumerator, e.g. "enum { A, B, };"
def p_enumerator_list_trailing_comma(p):
    "enumerator_list : enumerator_list COMMA"
    p[0] = p[1]


# a bare type declaration with no variables, e.g. "struct Point { ... };" or "enum Color;"
def p_declaration_bare_type(p):
    "declaration : type_specifier SEMI"
    p[0] = Declaration(p[1], [], line=p[1].line)


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


# Each leading '*' wraps the inner declarator, so "int **pp" and "int *arr[3]"
# fall out of this single rule without touching the identifier/array/function ones above.
def p_declarator_pointer(p):
    "declarator : MULTIPLY declarator"
    inner = p[2]
    inner.pointer_level += 1
    p[0] = inner


# function-pointer declarator, e.g. "int (*fp)(int, int)".
def p_declarator_function_pointer(p):
    "declarator : LPAREN MULTIPLY IDENTIFIER RPAREN LPAREN parameter_list_opt RPAREN"
    p[0] = Declarator(p[3], kind_name="function_pointer", params=p[6], pointer_level=1, line=p.lineno(3))

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


def p_parameter_list_variadic(p):
    "parameter_list : parameter_list COMMA ELLIPSIS"
    p[0] = p[1] + [VarArgsParameter(p.lineno(3))]


def p_parameter_list_single(p):
    "parameter_list : parameter"
    p[0] = [p[1]]


def p_parameter(p):
    "parameter : type_specifier declarator"
    p[0] = Parameter(p[1], p[2], p[2].line)


# An unnamed (abstract) parameter, e.g. "int f(int, int);" or a function
# pointer *type* such as "int (*fp)(int, int);". This is also how a sole
# "void" parameter list ("int f(void)") parses: as one unnamed parameter of
# type void, same as the standard C grammar - it is up to a later semantic
# pass, not the grammar, to treat that single case as "no parameters".
def p_parameter_unnamed(p):
    "parameter : type_specifier"
    p[0] = Parameter(p[1], None, p[1].line)


def p_statement(p):
    """statement : expression_statement
                 | compound_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
                 | labeled_statement
                 | declaration"""
    p[0] = p[1]


# Panic-mode recovery: on a malformed statement, discard tokens up to the
# next ';' and resume there, instead of re-reporting an error for every
# token in between. Standard yacc/PLY pattern (see the PLY manual's error
# token examples) - the AST for a source file with any syntax error is
# discarded by main.py regardless, so this rule exists purely to keep the
# reported error list to one entry per genuine problem.
def p_statement_error(p):
    "statement : error SEMI"
    p[0] = None
    parser.errok()


def p_compound_statement(p):
    "compound_statement : LBRACE block_item_list_opt RBRACE"
    p[0] = CompoundStatement(p[2], p.lineno(1))


def p_block_item_list_opt(p):
    """block_item_list_opt : block_item_list
                           | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_block_item_list_recursive(p):
    "block_item_list : block_item_list block_item"
    # block_item is None only for a recovered "error SEMI" - drop it rather
    # than adding a hole to the statement list.
    p[0] = p[1] if p[2] is None else p[1] + [p[2]]


def p_block_item_list_single(p):
    "block_item_list : block_item"
    p[0] = [] if p[1] is None else [p[1]]


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


def p_selection_statement_switch(p):
    "selection_statement : SWITCH LPAREN expression RPAREN LBRACE switch_case_list RBRACE"
    p[0] = SwitchStatement(p[3], p[6], p.lineno(1))


def p_selection_statement_switch_empty(p):
    "selection_statement : SWITCH LPAREN expression RPAREN LBRACE RBRACE"
    p[0] = SwitchStatement(p[3], [], p.lineno(1))


def p_switch_case_list_recursive(p):
    "switch_case_list : switch_case_list switch_case"
    p[0] = p[1] + [p[2]]


def p_switch_case_list_single(p):
    "switch_case_list : switch_case"
    p[0] = [p[1]]


def p_switch_case_labeled(p):
    "switch_case : CASE expression COLON block_item_list_opt"
    p[0] = SwitchCase(p[2], p[4], p.lineno(1))


def p_switch_case_default(p):
    "switch_case : DEFAULT COLON block_item_list_opt"
    p[0] = SwitchCase(None, p[3], p.lineno(1))


def p_iteration_statement_while(p):
    "iteration_statement : WHILE LPAREN expression RPAREN statement"
    p[0] = WhileStatement(p[3], p[5], p.lineno(1))


def p_iteration_statement_do_while(p):
    "iteration_statement : DO statement WHILE LPAREN expression RPAREN SEMI"
    p[0] = DoWhileStatement(p[2], p[5], p.lineno(1))

# "until (cond) stmt" repeats while cond is false - sugar for "while (!cond)".
def p_iteration_statement_until(p):
    "iteration_statement : UNTIL LPAREN expression RPAREN statement"
    p[0] = UntilStatement(p[3], p[5], p.lineno(1))


def p_iteration_statement_do_until(p):
    "iteration_statement : DO statement UNTIL LPAREN expression RPAREN SEMI"
    p[0] = DoUntilStatement(p[2], p[5], p.lineno(1))

# All three for-loop expressions are optional, allowing forms such as for (;;).
def p_iteration_statement_for(p):
    "iteration_statement : FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement"
    p[0] = ForStatement(p[3], p[5], p[7], p[9], p.lineno(1))


# A declaration in the for-init slot, e.g. "for (int i = 0; i < 3; i++)".
# The declaration nonterminal already ends in its own SEMI, so this mirrors
# the plain form but swaps "expression_opt SEMI" for "declaration" - the
# same choice the standard C99 grammar makes for for-loops.
def p_iteration_statement_for_declaration(p):
    "iteration_statement : FOR LPAREN declaration expression_opt SEMI expression_opt RPAREN statement"
    p[0] = ForStatement(p[3], p[4], p[6], p[8], p.lineno(1))


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
                             | unary_expression MOD_ASSIGN assignment_expression
                             | unary_expression AND_ASSIGN assignment_expression
                             | unary_expression OR_ASSIGN assignment_expression
                             | unary_expression XOR_ASSIGN assignment_expression
                             | unary_expression LSHIFT_ASSIGN assignment_expression
                             | unary_expression RSHIFT_ASSIGN assignment_expression"""
    p[0] = Assignment(p[2], p[1], p[3], p.lineno(2))


def p_assignment_expression_conditional(p):
    "assignment_expression : conditional_expression"
    p[0] = p[1]


# Ternary "cond ? then : else". The RHS branches recurse into
# conditional_expression (not assignment_expression), matching the standard
# C grammar and keeping ?: lower precedence than assignment inside branches
# resolved via the explicit `expression` in the middle branch.
def p_conditional_expression_ternary(p):
    "conditional_expression : logical_or_expression QUESTION expression COLON conditional_expression"
    p[0] = ConditionalExpression(p[1], p[3], p[5], p.lineno(2))


def p_conditional_expression_plain(p):
    "conditional_expression : logical_or_expression"
    p[0] = p[1]


def p_logical_or_expression(p):
    """logical_or_expression : logical_or_expression OR logical_and_expression
                             | logical_and_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("||", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_logical_and_expression(p):
    """logical_and_expression : logical_and_expression AND inclusive_or_expression
                              | inclusive_or_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("&&", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


# Bitwise OR / XOR / AND, in standard C's precedence order (OR loosest,
# AND tightest of the three). Binary AND reuses the ADDRESS token ('&'),
# same as real C, since the lexer cannot tell "&" apart from "&&"'s cousin
# without knowing whether it's in a unary or binary position.
def p_inclusive_or_expression(p):
    """inclusive_or_expression : inclusive_or_expression BIT_OR exclusive_or_expression
                               | exclusive_or_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("|", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_exclusive_or_expression(p):
    """exclusive_or_expression : exclusive_or_expression BIT_XOR and_expression
                               | and_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("^", p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_and_expression(p):
    """and_expression : and_expression ADDRESS equality_expression
                      | equality_expression"""
    if len(p) == 4:
        p[0] = BinaryOp("&", p[1], p[3], p.lineno(2))
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
    """relational_expression : relational_expression LT shift_expression
                             | relational_expression LE shift_expression
                             | relational_expression GT shift_expression
                             | relational_expression GE shift_expression
                             | shift_expression"""
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], p.lineno(2))
    else:
        p[0] = p[1]


def p_shift_expression(p):
    """shift_expression : shift_expression LSHIFT additive_expression
                        | shift_expression RSHIFT additive_expression
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
                        | BIT_NOT unary_expression
                        | MINUS unary_expression %prec UMINUS
                        | PLUS unary_expression %prec UPLUS
                        | ADDRESS unary_expression
                        | SIZEOF unary_expression"""
    p[0] = UnaryOp(p[1], p[2], "prefix", p.lineno(1))


# Type cast, e.g. "(int *)malloc(n * sizeof(int))". Tried only when the
# parenthesized content starts with a type keyword/typename, so it never
# competes with a plain "(expr)" grouping - the two productions start with
# disjoint token sets (INT/CHAR/VOID/STRUCT/UNION/ENUM/TYPENAME vs. anything
# that can begin an expression).
def p_unary_expression_cast(p):
    "unary_expression : LPAREN type_specifier pointer_opt RPAREN unary_expression %prec CAST"
    p[0] = CastExpression(p[2], p[3], p[5], p.lineno(1))


def p_pointer_opt_empty(p):
    "pointer_opt : empty"
    p[0] = 0


def p_pointer_opt_star(p):
    "pointer_opt : pointer_opt MULTIPLY"
    p[0] = p[1] + 1


# pointer dereference, e.g. "*p" or "**pp". %prec DEREF keeps this from being
# confused with the binary MULTIPLY operator at parse time.
def p_unary_expression_dereference(p):
    "unary_expression : MULTIPLY unary_expression %prec DEREF"
    p[0] = UnaryOp("*", p[2], "prefix", p.lineno(1))


def p_unary_expression_sizeof_type(p):
    "unary_expression : SIZEOF LPAREN type_specifier RPAREN"
    p[0] = UnaryOp("sizeof", p[3], "prefix", p.lineno(1))


# "new T", "new T[n]", "new T(args)" - dynamic allocation (C++ subset).
# The delimiter-less bare form ("new T" with nothing after it) can't use the
# general type_specifier: type_specifier includes a bare "class Dog"
# reference (class_specifier : class_head), whose own grammar already treats
# a following COLON as the start of a base-class list - so with nothing
# bounding it on the right, that ambiguity would leak into this rule's
# follow set. Parenthesized/bracketed new-expressions don't have this
# problem (RPAREN/RBRACKET already bounds them), so only the bare form needs
# the narrower new_bare_type_specifier below, which is every type_specifier
# alternative except a bare class reference - write "new Dog()" for that.
def p_unary_expression_new_plain(p):
    "unary_expression : NEW new_bare_type_specifier %prec NEW"
    p[0] = NewExpression(p[2], line=p.lineno(1))


def p_new_bare_type_specifier_builtin(p):
    "new_bare_type_specifier : builtin_type_seq"
    names, line = p[1]
    p[0] = TypeSpecifier(" ".join(names), line)


def p_new_bare_type_specifier_typename(p):
    "new_bare_type_specifier : TYPENAME"
    p[0] = TypeSpecifier(str(p[1]), p.lineno(1))


def p_new_bare_type_specifier_struct(p):
    "new_bare_type_specifier : struct_specifier"
    p[0] = p[1]


def p_new_bare_type_specifier_enum(p):
    "new_bare_type_specifier : enum_specifier"
    p[0] = p[1]


def p_new_bare_type_specifier_const(p):
    "new_bare_type_specifier : CONST new_bare_type_specifier"
    inner = p[2]
    if isinstance(inner, TypeSpecifier):
        p[0] = TypeSpecifier("const " + inner.name, p.lineno(1))
    else:
        inner.is_const = True
        p[0] = inner


def p_unary_expression_new_array(p):
    "unary_expression : NEW type_specifier LBRACKET expression RBRACKET %prec NEW"
    p[0] = NewExpression(p[2], count=p[4], line=p.lineno(1))


def p_unary_expression_new_args(p):
    "unary_expression : NEW type_specifier LPAREN argument_expression_list_opt RPAREN %prec NEW"
    p[0] = NewExpression(p[2], args=p[4], line=p.lineno(1))


# "delete p" / "delete[] p" - free-store deallocation (C++ subset).
def p_unary_expression_delete(p):
    "unary_expression : DELETE unary_expression %prec DELETE"
    p[0] = DeleteExpression(p[2], is_array=False, line=p.lineno(1))


def p_unary_expression_delete_array(p):
    "unary_expression : DELETE LBRACKET RBRACKET unary_expression %prec DELETE"
    p[0] = DeleteExpression(p[4], is_array=True, line=p.lineno(1))


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


def p_postfix_expression_member(p):
    "postfix_expression : postfix_expression DOT IDENTIFIER"
    p[0] = MemberAccess(p[1], p[3], is_pointer=False, line=p.lineno(2))


def p_postfix_expression_arrow(p):
    "postfix_expression : postfix_expression ARROW IDENTIFIER"
    p[0] = MemberAccess(p[1], p[3], is_pointer=True, line=p.lineno(2))


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


def p_primary_expression_float(p):
    "primary_expression : FLOAT_CONSTANT"
    p[0] = make_literal("float", p[1], p.lineno(1))


# "true"/"false" are keywords, not identifiers, so they need their own rule.
def p_primary_expression_bool(p):
    """primary_expression : TRUE_KW
                          | FALSE_KW"""
    p[0] = make_literal("bool", str(p[1]), p.lineno(1))


def p_primary_expression_char(p):
    "primary_expression : CHAR_CONSTANT"
    p[0] = make_literal("char", p[1], p.lineno(1))


def p_primary_expression_string(p):
    "primary_expression : STRING_LITERAL"
    p[0] = make_literal("string", p[1], p.lineno(1))


def p_primary_expression_grouped(p):
    "primary_expression : LPAREN expression RPAREN"
    p[0] = p[2]


# "ClassName::member" - scope-resolved access to a static member or an
# explicitly-qualified base member, e.g. "Base::greet()" or "Animal::legs".
def p_primary_expression_qualified(p):
    "primary_expression : class_name SCOPE IDENTIFIER"
    p[0] = QualifiedName(p[1], p[3], p.lineno(2))


def p_empty(p):
    "empty :"
    p[0] = None


def p_error(p):
    if p is None:
        add_syntax_error("Syntax Error: unexpected end of input")
        return

    add_syntax_error(f"Syntax Error: unexpected token '{p.value}' at line {p.lineno}")
    # Deliberately no parser.errok() here: calling it in p_error() itself
    # tells PLY "treat this as already resolved", which just discards the
    # one offending token and keeps parsing in the same (still-broken)
    # state - the token-by-token error cascade this project doesn't want.
    # Leaving normal error handling to run lets PLY unwind the parse stack
    # to the nearest "error SEMI" rule (see p_statement_error and
    # p_external_declaration_error) and resynchronize there instead;
    # errok() is called in those rules' own actions once that has happened.


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