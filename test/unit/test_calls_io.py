"""Unit tests: calls, recursion, scanf lowering, argv and atoi."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_tac_basic import body, compile_ir, run_c  # noqa: E402
from phase3_intermediate_code.tac_interpreter import run_ir  # noqa: E402


def test_spec_factorial_shape():
    ir = compile_ir("int fact(int n) { if (n > 1) return n * fact(n - 1); return 1; }\n"
                    "int main(void) { return fact(3); }")
    assert "func fact(int n) : int" in ir
    assert "param t1" in ir and "t2 = call fact, 1" in ir


def test_args_evaluated_before_params():
    ir = compile_ir("int f(int a, int b) { return a; }\n"
                    "int main(void) { return f(1 + f(2, 3), 4); }")
    main = ir.split("func main")[1]
    assert main.index("call f, 2") < main.index("param 4")


def test_scanf_lowering_matches_spec():
    ir = compile_ir('int main(void) { int x; scanf("%d", &x); return 0; }')
    b = body(ir)
    assert b[:3] == ["t1 = call read_int, 0", "t2 = call scan_status, 0", "if t2 == 0 goto L2"]
    assert "x = t1" in b


def test_scanf_space_c_skips_white_space():
    assert run_c('int main(void){char c; scanf(" %c", &c); printf("%c", c); return 0;}',
                 stdin=b"  \n\tq") == b"q"
    assert run_c('int main(void){char c; scanf("%c", &c); printf("%d", c); return 0;}',
                 stdin=b" q") == b"32"


def test_argv_and_atoi():
    ir = compile_ir('int main(int argc, char *argv[]) { return atoi(argv[1]) + argv[1][0]; }')
    assert run_ir(ir, ["7"], b"")[1] == 7 + ord("7")


def test_char_array_accepts_string_literal_argument():
    assert run_c('int n(char s[]) { int i = 0; while (s[i]) i++; return i; }\n'
                 'int main(void) { printf("%d", n("four")); return 0; }') == b"4"


def test_value_of_void_call_not_stored():
    ir = compile_ir("void f(void) { }\nint main(void) { f(); return 0; }")
    assert "    call f, 0" in ir and "= call f" not in ir
