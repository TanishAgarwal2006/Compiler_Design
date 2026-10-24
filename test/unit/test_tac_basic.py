"""Unit tests: IR generation for straight-line code and the TAC interpreter."""
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.errors import clear_errors, semantic_errors  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402
from phase3_intermediate_code import tac  # noqa: E402
from phase3_intermediate_code.semantic_analyzer import analyze  # noqa: E402
from phase3_intermediate_code.ir_generator import generate, GenError, NotYetImplemented  # noqa: E402
from phase3_intermediate_code.tac_interpreter import run_ir, IRError, RunError  # noqa: E402


def compile_ir(src):
    clear_errors()
    ast = parse_source(src)
    assert ast is not None, "program does not parse"
    result = analyze(ast)
    assert not semantic_errors, semantic_errors
    return tac.format_module(generate(ast, result))


def body(ir):
    """Instruction lines of the first function, stripped."""
    lines = ir.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("func "))
    out = []
    for l in lines[start + 1:]:
        if l == "endfunc":
            break
        if l.startswith("    local") or l.startswith("    temp"):
            continue
        out.append(l.strip())
    return out


def run_c(src, args=(), stdin=b""):
    return run_ir(compile_ir(src), args, stdin)[0]


# --- text layout -------------------------------------------------------------
def test_spec_float_example():
    ir = compile_ir("int main(void) { float f = 1.5; int i = 2; f = f + i; return 0; }")
    assert body(ir) == ["f = 1.5", "i = 2", "t1 = i2f i", "t2 = f +f t1", "f = t2", "return 0"]


def test_file_layout():
    ir = compile_ir('int g = 5;\nint main(void) { int y; y = g + 1; printf("v=%d\\n", y); return 0; }')
    assert ir.splitlines() == [
        ".data", 'str0: "v="', 'str1: "\\n"', "global g : int = 5", ".text",
        "func main() : int", "    local int y", "    temp t1:int",
        "    t1 = g + 1", "    y = t1",
        "    param str0", "    call print_str, 1",
        "    param y", "    call print_int, 1",
        "    param str1", "    call print_str, 1",
        "    return 0", "endfunc",
    ]


def test_params_and_return_header():
    ir = compile_ir("float half(int n, char c) { return n / 2.0; }\n"
                    "int main(int argc, char *argv[]) { return 0; }")
    assert "func half(int n, char c) : float" in ir
    assert "func main(int argc, str argv[]) : int" in ir
    assert body(ir) == ["t1 = i2f n", "t2 = t1 /f 2.0", "return t2"]


def test_void_function_gets_implicit_return():
    ir = compile_ir("void f(void) { int a; a = 1; }\nint main(void) { return 0; }")
    assert body(ir)[-1] == "return"


def test_missing_return_in_int_function_returns_zero():
    ir = compile_ir("int f(void) { int a; a = 1; }\nint main(void) { return 0; }")
    assert body(ir)[-1] == "return 0"


# --- expression lowering -----------------------------------------------------
def test_constants_are_folded_by_the_analyzer():
    ir = compile_ir("int main(void) { int a; a = 2 * 3 + 4; return 0; }")
    assert body(ir)[:1] == ["a = 10"]


def test_char_store_narrows_and_load_does_not():
    ir = compile_ir("int main(void) { char c = 'A'; int i; i = c + 1; c = i; return 0; }")
    assert body(ir) == ["c = 65", "t1 = c + 1", "i = t1", "t2 = i2c i", "c = t2", "return 0"]


def test_postfix_value_vs_statement():
    ir = compile_ir("int main(void) { int a = 1, b; b = a++; a++; return 0; }")
    assert body(ir) == ["a = 1", "t1 = a", "t2 = a + 1", "a = t2", "b = t1",
                        "t3 = a + 1", "a = t3", "return 0"]


def test_not_on_float_compares_with_zero():
    ir = compile_ir("int main(void) { float f = 0.5; int i; i = !f; return 0; }")
    assert "t1 = f ==f 0.0" in body(ir)


def test_float_to_char_goes_through_int():
    ir = compile_ir("int main(void) { float f = 2.5; char c; c = f; return 0; }")
    assert body(ir)[1:4] == ["t1 = f2i f", "t2 = i2c t1", "c = t2"]


def test_compound_assignment_with_float_value_on_int_target():
    ir = compile_ir("int main(void) { int i = 4; i *= 1.5; return 0; }")
    assert body(ir)[1:5] == ["t1 = i2f i", "t2 = t1 *f 1.5", "t3 = f2i t2", "i = t3"]


# --- names -------------------------------------------------------------------
def test_every_temp_is_declared_and_used():
    ir = compile_ir("int main(void) { int a = 3; float f = 1.5; f = f * a + (a - 1) / 2; return 0; }")
    lines = ir.splitlines()
    declared = set()
    for l in lines:
        if l.startswith("    temp"):
            declared |= {p.split(":")[0].strip() for p in l.replace("temp", "").split(",")}
    text = " ".join(body(ir))
    for t in declared:
        assert t in text.split() or f" {t} " in f" {text} ", t
    used = {w for w in text.replace("=", " ").split() if w.startswith("t") and w[1:].isdigit()}
    assert used <= declared


def test_variables_named_like_temps_and_ir_words_still_work():
    out = run_c('#include <stdio.h>\n'
                'int main(void) { int t1 = 3, str0 = 4, param = 1, inf = 2, call = 5;\n'
                '  printf("%d\\n", t1 + str0 + param + inf + call); return 0; }')
    assert out == b"15\n"


def test_string_labels_dedupe_and_avoid_variable_names():
    ir = compile_ir('int str0 = 1;\nint main(void) { printf("a"); printf("a"); return str0; }')
    assert ir.count('"a"') == 1
    assert 'str1: "a"' in ir


# --- generator limits --------------------------------------------------------
def test_printf_value_is_rejected():
    clear_errors()
    ast = parse_source('int main(void) { int n = printf("x"); return 0; }')
    result = analyze(ast)
    try:
        generate(ast, result)
    except NotYetImplemented:
        raise AssertionError("should be a plain GenError")
    except GenError as exc:
        assert "returned by printf" in exc.message


# --- end to end ----------------------------------------------------------------
def test_end_to_end_conversions():
    out = run_c('#include <stdio.h>\n'
                'int main(void) { char c = 200; int i = 300; float f = -2.7; char e;\n'
                '  e = i; printf("%d %d %d %d\\n", c, e, (int)f, (char)321); return 0; }')
    assert out == b"-56 44 -2 65\n"


def test_main_exit_code():
    _, code = run_ir(compile_ir("int main(void) { return 7; }"))
    assert code == 7


# --- interpreter on hand-written IR -----------------------------------------------
FACT_IR = """.data
.text
func fact(int n) : int
    temp t1:int, t2:int, t3:int
    if n > 1 goto L1
    return 1
L1:
    t1 = n - 1
    param t1
    t2 = call fact, 1
    t3 = n * t2
    return t3
endfunc
func main() : int
    temp t1:int
    param 10
    t1 = call fact, 1
    param t1
    call print_int, 1
    return 0
endfunc
"""


def test_interpreter_recursion():
    assert run_ir(FACT_IR)[0] == b"3628800"


def test_interpreter_deep_recursion():
    ir = FACT_IR.replace("param 10", "param 5000")
    out, _ = run_ir(ir)           # overflows to some int, but must not crash
    assert out.lstrip(b"-").isdigit()


def test_interpreter_loop_and_arrays():
    ir = """.data
.text
func main() : int
    local int a[4]
    local int i
    temp t1:int, t2:int, t3:int
    i = 0
L1:
    if i >= 4 goto L2
    t1 = i * 4
    t2 = i * i
    a[t1] = t2
    i = i + 1
    goto L1
L2:
    t3 = a[12]
    param t3
    call print_int, 1
    return 0
endfunc
"""
    assert run_ir(ir)[0] == b"9"


def test_interpreter_char_and_string_memory():
    ir = """.data
str0: "hi\\n"
.text
func main() : int
    local char c
    local str s
    temp t1:char, t2:int
    s = str0
    t1 = s[1]
    c = t1
    t2 = c + 0
    param t2
    call print_int, 1
    param s
    call print_str, 1
    return 0
endfunc
"""
    assert run_ir(ir)[0] == b"105hi\n"


def test_interpreter_io_and_argv():
    ir = """.data
.text
func main(int argc, str argv[]) : int
    local int n
    local str a
    temp t1:int, t2:str, t3:int
    t1 = call read_int, 0
    n = t1
    t2 = argv[4]
    a = t2
    t3 = call atoi, 1
    return 0
endfunc
""".replace("    t3 = call atoi, 1", "    param a\n    t3 = call atoi, 1\n    t3 = t3 + n\n    param t3\n    call print_int, 1")
    assert run_ir(ir, ["20"], b"  22\n")[0] == b"42"


def test_interpreter_float_semantics():
    ir = """.data
.text
func main() : int
    local float f
    temp t1:float, t2:int
    f = 16777216.0
    t1 = f +f 1.0
    param t1
    call print_float, 1
    t2 = f2i t1
    param t2
    call print_int, 1
    return 0
endfunc
"""
    assert run_ir(ir)[0] == b"16777216.00000016777216"      # 2**24 + 1 is not a float


def test_interpreter_int_semantics():
    ir = """.data
.text
func main() : int
    temp t1:int, t2:int, t3:int, t4:int
    t1 = -7 / 2
    t2 = -7 % 2
    t3 = 2147483647 + 1
    t4 = -8 >> 1
    param t1
    call print_int, 1
    param t2
    call print_int, 1
    param t3
    call print_int, 1
    param t4
    call print_int, 1
    return 0
endfunc
"""
    assert run_ir(ir)[0] == b"-3-1-2147483648-4"


def expect_error(ir, exc_type, fragment):
    try:
        run_ir(ir)
    except exc_type as exc:
        assert fragment in str(exc), str(exc)
        return
    raise AssertionError(f"expected {exc_type.__name__} containing {fragment!r}")


def test_interpreter_strictness():
    head = ".data\n.text\nfunc main() : int\n    local int x\n    local float f\n    temp t1:int\n"
    tail = "    return 0\nendfunc\n"
    expect_error(head + "    goto L9\n" + tail, IRError, "undefined label")
    expect_error(head + "    y = 1\n" + tail, IRError, "undefined name")
    expect_error(head + "    t1 = x +f 1.0\n" + tail, IRError, "needs float")
    expect_error(head + "    f = x\n" + tail, IRError, "copy")
    expect_error(head + "    param 1\n    call print_int, 2\n" + tail, IRError, "takes 1")
    expect_error(head + "    call print_int, 1\n" + tail, IRError, "before it")
    expect_error(head + "    param 1.5\n    call print_int, 1\n" + tail, IRError, "wrong type")
    expect_error(head + "    t1 = 1 / 0\n" + tail, RunError, "division by zero")


def test_interpreter_step_limit():
    ir = ".data\n.text\nfunc main() : int\nL1:\n    goto L1\nendfunc\n"
    try:
        run_ir(ir, max_steps=1000)
    except RunError as exc:
        assert "step limit" in str(exc)
    else:
        raise AssertionError("expected a step limit error")


def test_string_escapes_round_trip():
    data = bytes(range(0, 256))
    text = f'.data\nstr0: "{tac.escape_bytes(data)}"\n.text\nfunc main() : int\n    param str0\n    call print_str, 1\n    return 0\nendfunc\n'
    # print_str stops at the first NUL, so check the part before it and a later string separately
    out, _ = run_ir(text.replace(tac.escape_bytes(data), tac.escape_bytes(data[1:])))
    assert out == data[1:]


# --- command line ------------------------------------------------------------------
def test_cli_compile_and_run():
    with tempfile.TemporaryDirectory() as d:
        c = pathlib.Path(d) / "p.c"
        ir = pathlib.Path(d) / "sub" / "p.ir"
        c.write_text('int main(void) { printf("hello %d\\n", 6 * 7); return 3; }')
        r = subprocess.run([sys.executable, str(SRC / "main.py"), str(c), "--tac", "-o", str(ir)],
                           capture_output=True, text=True, cwd=ROOT)
        assert r.returncode == 0 and ir.exists(), r.stdout + r.stderr
        r = subprocess.run([sys.executable, str(SRC / "phase3_intermediate_code" / "tac_interpreter.py"),
                            str(ir)], capture_output=True, cwd=ROOT)
        assert r.stdout == b"hello 42\n" and r.returncode == 3


def test_cli_tac_to_stdout_is_only_ir():
    with tempfile.TemporaryDirectory() as d:
        c = pathlib.Path(d) / "p.c"
        c.write_text("int main(void) { return 0; }")
        r = subprocess.run([sys.executable, str(SRC / "main.py"), str(c), "--tac"],
                           capture_output=True, text=True, cwd=ROOT)
        assert r.returncode == 0 and r.stdout.startswith(".data\n"), r.stdout


def test_cli_error_writes_no_ir_file():
    with tempfile.TemporaryDirectory() as d:
        c = pathlib.Path(d) / "p.c"
        ir = pathlib.Path(d) / "p.ir"
        c.write_text("int main(void) { return x; }")
        r = subprocess.run([sys.executable, str(SRC / "main.py"), str(c), "--tac", "-o", str(ir)],
                           capture_output=True, text=True, cwd=ROOT)
        assert r.returncode == 1 and not ir.exists()
        assert ":1: semantic error:" in r.stderr and "1 error found" in r.stderr
