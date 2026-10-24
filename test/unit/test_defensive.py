"""Unit tests: the defensive error branches that no C source can reach.

The lexer and parser already refuse most bad input, so these branches of the semantic analyzer and the IR
generator can only be hit with a tree that was edited by hand. Each test parses a good program, breaks one
node and checks that the stage reports a clear error instead of crashing.
"""
import copy
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.errors import clear_errors, semantic_errors  # noqa: E402
from phase2_syntax_analysis.ast_nodes import ASTNode, Identifier  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402
from phase3_intermediate_code.ir_generator import generate, ir_type, GenError  # noqa: E402
from phase3_intermediate_code.semantic_analyzer import analyze  # noqa: E402
from phase3_intermediate_code.type_system import ERROR  # noqa: E402


def tree(src):
    clear_errors()
    ast = parse_source(src)
    assert ast is not None
    return ast


def find(node, kind, out=None):
    out = [] if out is None else out
    if isinstance(node, list):
        for x in node:
            find(x, kind, out)
    elif isinstance(node, ASTNode):
        if node.kind == kind:
            out.append(node)
        for v in vars(node).values():
            find(v, kind, out)
    return out


def errors_of(ast):
    clear_errors()
    analyze(ast)
    return " | ".join(semantic_errors)


MAIN = "int main(void) { return 0; }\n"


def test_unknown_top_level_item():
    ast = tree(MAIN)
    ast.declarations.append(ASTNode("Weird", 1))
    assert "unsupported feature: Weird" in errors_of(ast)


def test_unknown_statement():
    ast = tree(MAIN)
    find(ast, "CompoundStatement")[0].items.append(ASTNode("Weird", 1))
    assert "unsupported feature: Weird" in errors_of(ast)


def test_member_function_declarator():
    ast = tree("int g;\n" + MAIN)
    find(ast, "Declarator")[0].scope = "Dog"
    assert "member functions" in errors_of(ast)


def test_function_declarator_with_array_suffix():
    ast = tree("int f(void);\n" + MAIN)
    decl = next(d for d in find(ast, "Declarator") if d.name == "f")
    decl.dimensions = copy.deepcopy(find(tree("int a[3];"), "ArrayDimension"))
    assert "cannot return an array" in errors_of(ast)


def test_bad_literal_text():
    ast = tree('int main(void) { char *s = "x"; return 0; }\n')
    find(ast, "Literal")[0].value = "no quotes"
    assert "not a string literal" in errors_of(ast)


def test_unknown_literal_type():
    ast = tree("int main(void) { int x = 1; return x; }\n")
    find(ast, "Literal")[0].literal_type = "weird"
    assert "unknown literal type 'weird'" in errors_of(ast)


def test_typedef_name_used_as_value():
    ast = tree("typedef int T;\nint main(void) { int x = 1; return x; }\n")
    find(ast, "Declaration")[1].declarators[0].initializer = Identifier("T", 2)
    assert "type name 'T' used as a value" in errors_of(ast)


def test_unknown_assignment_operator():
    ast = tree("int main(void) { int x = 1; x += 1; return x; }\n")
    find(ast, "Assignment")[0].operator = "@="
    assert "unknown assignment operator '@='" in errors_of(ast)


def _generated(src, mutate):
    ast = tree(src)
    clear_errors()
    result = analyze(ast)
    assert not semantic_errors, semantic_errors
    mutate(ast)
    try:
        generate(ast, result)
    except GenError as exc:
        return exc.message
    raise AssertionError("generate() accepted a broken tree")


def test_generator_rejects_unknown_node():
    msg = _generated(MAIN, lambda a: find(a, "CompoundStatement")[0].items.append(ASTNode("Weird", 1)))
    assert "cannot generate code for Weird" in msg


def test_generator_rejects_unknown_literal():
    msg = _generated('int main(void) { char *s = "x"; return s[0]; }\n',
                     lambda a: setattr(find(a, "Literal")[0], "literal_type", "weird"))
    assert "literal of type weird has no value" in msg


def test_generator_rejects_unknown_unary_operator():
    msg = _generated("int main(void) { int x = 1; return -x; }\n",
                     lambda a: setattr(find(a, "UnaryOp")[0], "operator", "@"))
    assert "unary operator '@' is not supported" in msg


def test_ir_type_of_error_type():
    try:
        ir_type(ERROR)
    except GenError as exc:
        assert "no IR type" in exc.message
    else:
        raise AssertionError("ir_type(ERROR) must fail")
