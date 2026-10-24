"""Unit tests: the command-line driver (src/main.py) - every option, the exit codes and the file errors."""
import pathlib
import subprocess
import sys
import tempfile

MAIN = pathlib.Path(__file__).resolve().parents[2] / "src" / "main.py"

# One program that has every kind of name: function, parameter, array, plain variable, typedef and label.
PROGRAM = """typedef int Num;
int total = 3;
int add(int a, int b) { return a + b; }
int main(void) {
    int v[2] = {1, 2};
    Num s = add(v[0], total);
top:
    if (s > 100) goto top;
    printf("%d\\n", s);
    return 0;
}
"""


def run(source, *flags):
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d) / "prog.c"
        path.write_text(source)
        r = subprocess.run([sys.executable, str(MAIN), str(path), *flags], capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr


def test_default_run_reports_syntax_ok():
    code, out, _ = run(PROGRAM)
    assert code == 0 and "Syntax analysis: OK" in out
    assert "FUNCTION_NAME" in out and "LABEL_NAME" in out      # the classified token table is the default view


def test_tokens_only_stops_before_the_parser():
    code, out, _ = run(PROGRAM, "--tokens")
    assert code == 0 and "Token table (lexical analysis):" in out and "IDENTIFIER" in out
    assert out.rstrip().endswith("no lexical errors")
    assert "Syntax analysis" not in out
    code, out, _ = run("int x = ;", "--tokens")                  # a grammar error is invisible to Phase 1 alone
    assert code == 0


def test_all_name_roles_are_labelled():
    code, out, _ = run(PROGRAM, "--all")
    assert code == 0
    for label in ("FUNCTION_NAME", "VARIABLE_NAME", "PARAMETER_NAME", "ARRAY_NAME", "LABEL_NAME", "TYPENAME"):
        assert label in out, label
    assert "Symbol report:" in out and "Abstract syntax tree:" in out


def test_symbols_report():
    code, out, _ = run(PROGRAM, "--symbols")
    assert code == 0 and "Symbol report:" in out
    for role in ("function", "parameter", "array", "variable", "label", "typedef"):
        assert any(line.split()[1:2] == [role] for line in out.splitlines() if line.strip()), role
    assert "dims: [2]" in out and "params: (int, int)" in out


def test_ast_dump():
    code, out, _ = run(PROGRAM, "--ast")
    assert code == 0 and "Abstract syntax tree:" in out
    assert "FunctionDefinition" in out and "ArrayAccess" in out and "LabeledStatement" in out


def test_semantic_table():
    code, out, _ = run(PROGRAM, "--semantic")
    assert code == 0 and "Semantic analysis: OK" in out
    assert "Global variables" in out and "Function main: parameters and locals" in out
    assert "Typedefs" in out and "Num" in out and "Enum constants" in out


def test_tac_printed_and_written():
    code, out, _ = run(PROGRAM, "--tac")
    assert code == 0 and out.startswith(".data") and "func main() : int" in out and "call add, 2" in out
    with tempfile.TemporaryDirectory() as d:
        src, ir = pathlib.Path(d) / "p.c", pathlib.Path(d) / "sub" / "p.ir"
        src.write_text(PROGRAM)
        r = subprocess.run([sys.executable, str(MAIN), str(src), "-o", str(ir)], capture_output=True, text=True)
        assert r.returncode == 0 and "IR written to" in r.stdout
        assert ir.read_text().startswith(".data")                # the missing 'sub' folder was created


def test_errors_exit_1_and_write_nothing():
    for source, kind in (("int x = 'ab';", "lexical error"), ("int x = ;", "syntax error"),
                         ("int main(void) { return y; }", "semantic error"),
                         ("int f(int r[2]) { return r[0]; }\n"
                          "int main(void) { int m[2][2]; return f(m[1]); }", "unsupported feature")):
        with tempfile.TemporaryDirectory() as d:
            src, ir = pathlib.Path(d) / "p.c", pathlib.Path(d) / "p.ir"
            src.write_text(source)
            r = subprocess.run([sys.executable, str(MAIN), str(src), "-o", str(ir)], capture_output=True, text=True)
            assert r.returncode == 1 and kind in r.stderr and "No output was produced." in r.stderr, (source, r.stderr)
            assert not ir.exists()


def test_missing_source_file():
    r = subprocess.run([sys.executable, str(MAIN), "/no/such/file.c"], capture_output=True, text=True)
    assert r.returncode == 1 and "cannot read '/no/such/file.c'" in r.stderr
