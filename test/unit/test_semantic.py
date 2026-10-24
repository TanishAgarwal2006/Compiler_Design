"""Unit tests: type system, symbol table, semantic analyzer annotations."""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.errors import clear_errors, semantic_errors  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402
from phase3_intermediate_code import type_system as T  # noqa: E402
from phase3_intermediate_code.semantic_analyzer import (  # noqa: E402
    analyze, parse_format, fold_binary, wrap32, convert_const,
)


def run(src):
    clear_errors()
    ast = parse_source(src)
    assert ast is not None, "program does not parse"
    result = analyze(ast)
    return ast, result


def find(node, kind, out=None):
    out = [] if out is None else out
    if isinstance(node, list):
        for x in node:
            find(x, kind, out)
    elif hasattr(node, "kind") and isinstance(getattr(node, "kind"), str) and hasattr(node, "line"):
        if node.kind == kind:
            out.append(node)
        for v in vars(node).values():
            if isinstance(v, list) or (hasattr(v, "kind") and hasattr(v, "line")):
                find(v, kind, out)
    return out


# --- type system -----------------------------------------------------------
def test_types_structural_equality_and_width():
    assert T.ArrayType(T.INT, (3, 4)) == T.ArrayType(T.INT, (3, 4))
    assert T.ArrayType(T.INT, (3, 4)) != T.ArrayType(T.INT, (4, 3))
    assert T.ArrayType(T.INT, (3, 4)).width == 48
    assert T.ArrayType(T.CHAR, (10,)).width == 10
    assert T.ArrayType(T.INT, (None, 4)).width == 4       # parameter: one address
    assert T.ArrayType(T.INT, (3, 4)).row_type() == T.ArrayType(T.INT, (4,))
    assert T.ArrayType(T.INT, (4,)).row_type() == T.INT
    assert T.FunctionType(T.INT, (T.INT, T.STRING)) == T.FunctionType(T.INT, (T.INT, T.STRING))


def test_type_rules():
    assert T.common_arithmetic(T.INT, T.CHAR) == T.INT
    assert T.common_arithmetic(T.INT, T.FLOAT) == T.FLOAT
    assert T.promote(T.CHAR) == T.INT and T.promote(T.FLOAT) == T.FLOAT
    assert T.assignable(T.FLOAT, T.INT) and T.assignable(T.CHAR, T.INT)
    assert not T.assignable(T.INT, T.ArrayType(T.INT, (3,)))
    assert T.assignable(T.STRING, T.ArrayType(T.CHAR, (4,)))
    assert not T.assignable(T.INT, T.VOID)
    assert T.assignable(T.INT, T.ERROR)


# --- symbol table ------------------------------------------------------------
def test_unique_ir_names_for_shadowing():
    _, r = run(
        "int x = 1;\n"
        "int f(int x) { int y = x; { int y = 2; y++; } return y; }\n"
        "int main(void) { int x = 5; { int x = 6; } return f(x); }\n"
    )
    assert not r.errors
    f = r.functions["f"]
    assert [s.ir_name for s in f.params] == ["x.1"]          # clashes with global x
    assert [s.ir_name for s in f.locals] == ["y", "y.1"]
    m = r.functions["main"]
    assert [s.ir_name for s in m.locals] == ["x.1", "x.2"]


def test_offsets_and_frame_size():
    _, r = run("int main(void) { int a[3][4]; char s[10]; int i; float f; return 0; }")
    m = r.functions["main"]
    got = {s.name: (s.size, s.offset) for s in m.locals}
    assert got == {"a": (48, 0), "s": (10, 48), "i": (4, 60), "f": (4, 64)}
    assert m.frame_size == 68


def test_global_data_layout():
    _, r = run("int a = 1; char c = 'x'; int t[3] = {1,2,3}; int main(void) { return 0; }")
    got = [(s.name, s.size, s.offset) for s in r.globals]
    assert got == [("a", 4, 0), ("c", 1, 4), ("t", 12, 8)]


def test_params_and_locals_are_distinguished():
    _, r = run("int f(int a, char b) { int c = a; return c + b; } int main(void) { return f(1, 2); }")
    f = r.functions["f"]
    assert [(s.name, s.scope) for s in f.params] == [("a", "param"), ("b", "param")]
    assert [(s.name, s.scope) for s in f.locals] == [("c", "local")]


# --- constants and folding ----------------------------------------------------
def test_constant_folding_c_semantics():
    assert fold_binary("/", -7, 2, False) == -3
    assert fold_binary("%", -7, 2, False) == -1
    assert fold_binary("%", 7, -2, False) == 1
    assert fold_binary("+", 2 ** 31 - 1, 1, False) == -(2 ** 31)
    assert fold_binary("<<", 1, 31, False) == -(2 ** 31)
    assert fold_binary("/", 1, 0, False) is None
    assert fold_binary("/", 7, 2, True) == 3.5
    assert wrap32(2 ** 32 + 5) == 5
    assert convert_const(300, T.CHAR) == 44
    assert convert_const(3.9, T.INT) == 3
    assert convert_const(2, T.FLOAT) == 2.0


def test_const_values_on_expressions():
    ast, r = run("enum E { A = 2, B }; const int K = 4; int main(void) { int a[A + B * K]; return sizeof(a); }")
    assert not r.errors
    main = r.functions["main"]
    assert main.locals[0].type == T.ArrayType(T.INT, (14,))
    ret = find(ast, "ReturnStatement")[0]
    assert ret.value.const_value == 56


def test_array_size_inferred_from_initializer():
    _, r = run('int main(void) { int a[] = {1,2,3,4}; int m[][2] = {{1,2},{3,4},{5,6}}; char s[] = "hey"; return 0; }')
    assert not r.errors
    types = {s.name: s.type for s in r.functions["main"].locals}
    assert types["a"] == T.ArrayType(T.INT, (4,))
    assert types["m"] == T.ArrayType(T.INT, (3, 2))
    assert types["s"] == T.ArrayType(T.CHAR, (4,))


def test_initializer_flattening():
    ast, r = run("int main(void) { int m[2][2] = {{1,2},{3,4}}; int f[2][3] = {1,2,3,4,5,6}; return 0; }")
    assert not r.errors
    decls = find(ast, "InitDeclarator")
    nested = [(i, e.value) for i, e in decls[0].init_elems]
    flat = [(i, e.value) for i, e in decls[1].init_elems]
    assert nested == [(0, 1), (1, 2), (2, 3), (3, 4)]
    assert flat == [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    assert decls[0].init_kind == "array"


def test_string_initializer_elements():
    ast, r = run('int main(void) { char s[5] = "ab"; return 0; }')
    d = find(ast, "InitDeclarator")[0]
    assert d.init_kind == "string"
    assert d.init_elems == [(0, 97), (1, 98), (2, 0)]


# --- annotations -------------------------------------------------------------
def test_expression_types_and_conversions():
    ast, r = run("int main(void) { char c = 'a'; int i = 2; float f = 1.5; "
                 "int a = c + i; float b = i * f; int d = i < f; return 0; }")
    assert not r.errors
    ops = find(ast, "BinaryOp")
    assert [o.ctype for o in ops] == [T.INT, T.FLOAT, T.INT]


def test_call_annotations():
    ast, r = run("int f(int a) { return a; } int main(void) { return f(3); }")
    call = find(ast, "FunctionCall")[0]
    assert call.symbol.name == "f" and call.ctype == T.INT and call.builtin is None


def test_printf_format_items():
    ast, r = run('int main(void) { int n = 1; printf("n=%d %c 100%%\\n", n, 65); return 0; }')
    assert not r.errors
    call = find(ast, "FunctionCall")[0]
    kinds = [(it[0], it[1] if it[0] == "lit" else it[1]) for it in call.format_items]
    assert kinds == [("lit", b"n="), ("spec", "d"), ("lit", b" "), ("spec", "c"), ("lit", b" 100%\n")]
    assert call.builtin == "printf"


def test_scanf_format_items():
    ast, r = run('int main(void) { int n; char w[8]; int a[2]; scanf("%d", &n); scanf("%s", w); scanf("%d", &a[1]); return 0; }')
    assert not r.errors
    calls = find(ast, "FunctionCall")
    assert [c.format_items[0][1] for c in calls] == ["d", "s", "d"]
    assert calls[0].format_items[0][2].kind == "Identifier"
    assert calls[2].format_items[0][2].kind == "ArrayAccess"


def test_parse_format():
    assert parse_format(b"a%db") == [("lit", b"a"), ("spec", "d"), ("lit", b"b")]
    assert parse_format(b"%i") == [("spec", "d")]
    assert parse_format(b"100%%") == [("lit", b"100%")]
    for bad in (b"%5d", b"%.2f", b"%ld", b"%", b"%x"):
        try:
            parse_format(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} should be rejected")


def test_switch_case_values_recorded():
    ast, r = run("enum E { A = 3 }; int main(void) { int x = 1; switch (x) { case 1: break; case A: break; default: break; } return 0; }")
    assert not r.errors
    cases = find(ast, "SwitchCase")
    assert [c.const_value for c in cases] == [1, 3, None]


# --- error handling -------------------------------------------------------------
def test_one_mistake_gives_one_error():
    # the undeclared name must not cascade into follow-up type errors
    _, r = run("int main(void) { int a = nope + 1; int b = nope * a; return a + b; }")
    assert len(r.errors) == 2
    assert all("undeclared identifier 'nope'" in e for e in r.errors)


def test_errors_sorted_by_line_with_line_numbers():
    _, r = run("int main(void) {\n  return b;\n}\nint f(void) {\n  return a;\n}\n")
    assert [e.split(":")[0] for e in r.errors] == ["semantic error at line 2", "semantic error at line 5"]


def test_semantic_errors_reach_shared_list():
    run("int main(void) { return z; }")
    assert len(semantic_errors) == 1


def test_forward_goto_is_accepted():
    _, r = run("int main(void) { goto end; end: return 0; }")
    assert not r.errors


def test_args_and_strings():
    ast, r = run("int main(int argc, char *argv[]) { char *s = argv[1]; return atoi(s) + argv[1][0] + argc; }")
    assert not r.errors
    assert r.functions["main"].params[1].type == T.ArrayType(T.STRING, (None,))
    assert r.functions["main"].locals[0].type == T.STRING
