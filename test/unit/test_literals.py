"""Unit tests: literal helpers (characters, strings, escapes) and AST line numbers."""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.literals import char_value, string_bytes, literal_value  # noqa: E402
from common.errors import clear_errors  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402
from phase2_syntax_analysis.ast_nodes import ASTNode, Literal  # noqa: E402


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def test_char_value_plain_and_escapes():
    assert char_value("'a'") == 97
    assert char_value("'0'") == 48
    assert char_value("'\\n'") == 10
    assert char_value("'\\t'") == 9
    assert char_value("'\\0'") == 0
    assert char_value("'\\\\'") == 92
    assert char_value("'\\''") == 39
    assert char_value("'\"'") == 34


def test_char_value_rejects_bad_input():
    assert _raises(char_value, "'ab'")
    assert _raises(char_value, "'\\q'")
    assert _raises(char_value, "a")


def test_string_bytes_escapes():
    assert string_bytes('"hi"') == b"hi"
    assert string_bytes('""') == b""
    assert string_bytes('"a\\nb"') == b"a\nb"
    assert string_bytes('"tab\\there"') == b"tab\there"
    assert string_bytes('"q\\"q"') == b'q"q'
    assert string_bytes('"back\\\\slash"') == b"back\\slash"
    assert string_bytes('"\\x41\\102"') == b"AB"
    assert string_bytes('"%d\\n"') == b"%d\n"
    assert _raises(string_bytes, '"\\q"')   # unknown escape is rejected (the lexer reports it first)


def test_string_bytes_rejects_bad_input():
    assert _raises(string_bytes, "hi")
    assert _raises(string_bytes, '"abc\\"')


def test_literal_value_all_kinds():
    assert literal_value(Literal("int", 31, 1)) == 31
    assert literal_value(Literal("float", 1.5, 1)) == 1.5
    assert literal_value(Literal("char", "'A'", 1)) == 65
    assert literal_value(Literal("bool", "true", 1)) == 1
    assert literal_value(Literal("bool", "false", 1)) == 0
    assert literal_value(Literal("string", '"x\\n"', 1)) == b"x\n"


def _lines_missing(node, found):
    if isinstance(node, list):
        for item in node:
            _lines_missing(item, found)
    elif isinstance(node, ASTNode):
        if not node.line and node.kind != "Program":
            found.append(node.kind)
        for value in vars(node).values():
            if isinstance(value, (ASTNode, list)):
                _lines_missing(value, found)


def test_ast_nodes_carry_line_numbers():
    src = (
        "typedef int Count;\n"
        "const int K = 3;\n"
        "unsigned long int big;\n"
        "float f(float x) { return x; }\n"
        "int main(int argc, char *argv[]) {\n"
        "    int a[2][3];\n"
        "    for (int i = 0; i < 2; i++) { a[i][0] = i; }\n"
        "    return 0;\n"
        "}\n"
    )
    clear_errors()
    ast = parse_source(src)
    assert ast is not None
    missing = []
    _lines_missing(ast, missing)
    assert not missing, f"nodes without a line number: {missing}"
    decl = ast.declarations[1]
    assert decl.line == 2 and decl.type_spec.line == 2
    assert ast.declarations[2].type_spec.name == "unsigned long int"
    assert ast.declarations[2].line == 3
    func = ast.declarations[3]
    assert func.line == 4 and func.return_type.line == 4
    assert ast.declarations[4].line == 5


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  [PASS] {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  [FAIL] {name}  -- {exc}")
    sys.exit(1 if failures else 0)
