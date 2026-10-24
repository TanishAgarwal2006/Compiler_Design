"""Unit tests: every error message of the IR interpreter (bad IR files and faults while running)."""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase3_intermediate_code.tac_interpreter import run_ir, IRError, RunError  # noqa: E402


def main_with(body, header="func main() : int", pre=""):
    """A whole IR file whose only function is `header` with the given instruction lines."""
    return pre + ".text\n" + header + "\n" + "".join("    " + l + "\n" for l in body) + "endfunc\n"


INT_T1 = "temp t1:int"

# (name, IR text, exception, text the message must contain)
CASES = [
    ("modulo_by_zero", main_with([INT_T1, "t1 = 5 % 0", "return t1"]), RunError, "division by zero"),
    ("string_ends_with_backslash", '.data\ns0: "ab\\"\n', IRError, "string ends with a backslash"),
    ("unknown_string_escape", '.data\ns0: "a\\q"\n', IRError, "unknown escape \\q"),
    ("no_section", "func main() : int\n", IRError, "expected .data or .text"),
    ("missing_endfunc", ".text\nfunc main() : int\n", IRError, "missing endfunc"),
    ("bad_data_line", ".data\nbogus\n", IRError, "cannot read data line"),
    ("bad_func_header", ".text\nnonsense\n", IRError, "expected a func header"),
    ("bad_parameter", main_with(["return 0"], "func main(int) : int"), IRError, "bad parameter"),
    ("function_twice", main_with(["return 0"]) + main_with(["return 0"]), IRError, "defined twice"),
    ("bad_temp", main_with(["temp t1", "return 0"]), IRError, "bad temp declaration"),
    ("global_twice", ".data\nglobal g : int\nglobal g : int\n" + main_with(["return 0"]), IRError, "global g defined twice"),
    ("name_twice", main_with(["local int x", "local int x", "return 0"]), IRError, "x declared twice"),
    ("undefined_name", main_with(["local int a", "a = zz", "return a"]), IRError, "undefined name zz"),
    ("undefined_destination", main_with(["zz = 1", "return 0"]), IRError, "undefined name zz"),
    ("assign_to_array", main_with(["local int a[2]", "a = 1", "return 0"]), IRError, "cannot assign to array a"),
    ("undefined_array", main_with(["local int a", "a = q[0]", "return a"]), IRError, "undefined name q"),
    ("not_an_array", main_with(["local int a", "a = a[0]", "return a"]), IRError, "a is not an array or string"),
    ("label_twice", main_with(["L1:", "L1:", "return 0"]), IRError, "label L1 defined twice"),
    ("param_without_call", main_with(["param 1", "return 0"]), IRError, "param without a call"),
    ("unreadable_instruction", main_with(["???", "return 0"]), IRError, "cannot read instruction"),
    ("unknown_comparison", main_with(["L1:", "if 1 ?? 2 goto L1", "return 0"]), IRError, "unknown comparison"),
    ("undefined_label", main_with(["goto L9", "return 0"]), IRError, "undefined label L9"),
    ("missing_return_value", main_with(["return"]), IRError, "main must return a value"),
    ("void_returns_value", main_with(["return 1"], "func f() : void") + main_with(["return 0"]), IRError, "f is void but returns a value"),
    ("call_undefined", main_with(["call nope, 0", "return 0"]), IRError, "call to undefined function nope"),
    ("call_wrong_count", main_with(["call print_int, 0", "return 0"]), IRError, "print_int takes 1 parameter(s)"),
    ("call_missing_param", main_with(["call print_int, 1", "return 0"]), IRError, "has only 0 param(s)"),
    ("call_wrong_type", main_with(["param 1.5", "call print_int, 1", "return 0"]), IRError, "argument 1 of print_int has the wrong type"),
    ("call_void_result", main_with([INT_T1, "param 1", "t1 = call print_int, 1", "return 0"]), IRError, "print_int returns no value"),
    ("unknown_unary", main_with([INT_T1, "t1 = @ 1", "return 0"]), IRError, "unknown unary operator @"),
    ("unknown_binary", main_with([INT_T1, "t1 = 1 @ 2", "return 0"]), IRError, "unknown operator @"),
    ("long_right_hand_side", main_with([INT_T1, "t1 = 1 + 2 3", "return 0"]), IRError, "cannot read right-hand side"),
    ("wrong_operand_class", main_with([INT_T1, "t1 = 1.5 + 2", "return 0"]), IRError, "operand 1.5 is float, but + needs int"),
    ("out_of_memory", main_with(["local int a[9999999]", "return 0"]), RunError, "out of memory"),
    ("memory_out_of_range", main_with(["local int a[2]", INT_T1, "t1 = a[99999999]", "return 0"]), RunError, "out of range"),
    ("bad_initial_value", ".data\nglobal g : int = xyz\n" + main_with(["return 0"]), IRError, "bad initial value xyz"),
    ("array_init_without_braces", ".data\nglobal g : int[2] = 5\n" + main_with(["return 0"]), IRError, "array initializer must be in braces"),
    ("no_main", main_with(["return 0"], "func other() : int"), IRError, "no main function"),
    ("bad_main_parameters", main_with(["return 0"], "func main(int a) : int"), IRError, "main must take no parameters"),
    ("falls_off_the_end", main_with([INT_T1, "t1 = 1"]), RunError, "control reaches the end of main"),
    ("endless_loop", main_with(["L1:", "goto L1"]), RunError, "step limit exceeded"),
    ("endless_recursion", main_with(["call main, 0", "return 0"]), RunError, "call stack too deep"),
]


def test_every_ir_error_message():
    bad = []
    for name, text, exc, wanted in CASES:
        try:
            run_ir(text, max_steps=10000 if name == "endless_loop" else 10**8)
        except exc as e:
            if wanted not in str(e):
                bad.append(f"{name}: wanted {wanted!r}, got {str(e)!r}")
        except Exception as e:  # any other exception type is a bug in the test or the interpreter
            bad.append(f"{name}: unexpected {e!r}")
        else:
            bad.append(f"{name}: no error raised")
    assert not bad, "\n".join(bad)
