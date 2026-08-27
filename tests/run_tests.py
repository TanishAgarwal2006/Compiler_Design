#!/usr/bin/env python3
"""
Automated test harness for the compiler.

Convention:
    tests/phase1_lexical/valid/*.c    -> must lex with ZERO lexical errors
    tests/phase1_lexical/invalid/*.c  -> must produce >=1 lexical error
    tests/phase2_syntax/valid/*.c     -> must lex AND parse with ZERO errors
    tests/phase2_syntax/invalid/*.c   -> must produce >=1 lexical/syntax error

Unlike the old run.sh (which just dumped raw output to a text file for a
human to eyeball), this script gives a pass/fail verdict for every file and
a non-zero exit code if anything regresses, so it can be wired into CI or
run before every commit: `python tests/run_tests.py`.
"""
import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = TESTS_DIR.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from phase1_lexical_analysis.lexer import build_lexer             # noqa: E402
from phase2_syntax_analysis.parser import parse_source    # noqa: E402
from common.errors import clear_errors, lex_errors, syntax_errors  # noqa: E402


def run_lexer_only(code: str):
    clear_errors()
    lexer = build_lexer()
    lexer.lineno = 1
    lexer.input(code)
    while lexer.token():
        pass
    return list(lex_errors)


def run_full_pipeline(code: str):
    clear_errors()
    ast = parse_source(code)
    return list(lex_errors), list(syntax_errors), ast


def check_phase1(path: pathlib.Path, expect_valid: bool) -> tuple[bool, str]:
    code = path.read_text()
    errors = run_lexer_only(code)
    ok = (not errors) if expect_valid else bool(errors)
    detail = "" if ok else f"expected {'no errors' if expect_valid else 'an error'}, got {errors}"
    return ok, detail


def check_phase2(path: pathlib.Path, expect_valid: bool) -> tuple[bool, str]:
    code = path.read_text()
    lex_errs, syn_errs, ast = run_full_pipeline(code)
    has_errors = bool(lex_errs or syn_errs) or ast is None
    ok = (not has_errors) if expect_valid else has_errors
    detail = "" if ok else f"expected {'success' if expect_valid else 'a failure'}, got lex={lex_errs} syntax={syn_errs}"
    return ok, detail


def run_suite(label: str, directory: pathlib.Path, expect_valid: bool, checker) -> tuple[int, int]:
    passed = 0
    total = 0
    for path in sorted(directory.glob("*.c")):
        total += 1
        ok, detail = checker(path, expect_valid)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}/{path.name}" + (f"  -- {detail}" if detail else ""))
        if ok:
            passed += 1
    return passed, total


def main() -> int:
    suites = [
        ("phase1_lexical/valid", TESTS_DIR / "phase1_lexical" / "valid", True, check_phase1),
        ("phase1_lexical/invalid", TESTS_DIR / "phase1_lexical" / "invalid", False, check_phase1),
        ("phase2_syntax/valid", TESTS_DIR / "phase2_syntax" / "valid", True, check_phase2),
        ("phase2_syntax/invalid", TESTS_DIR / "phase2_syntax" / "invalid", False, check_phase2),
    ]

    grand_passed = 0
    grand_total = 0
    print("=" * 60)
    print(" Compiler Test Suite")
    print("=" * 60)
    for label, directory, expect_valid, checker in suites:
        if not directory.exists():
            continue
        print(f"\n{label}  (expect {'valid' if expect_valid else 'invalid'} programs)")
        passed, total = run_suite(label, directory, expect_valid, checker)
        grand_passed += passed
        grand_total += total

    print("\n" + "=" * 60)
    print(f" Result: {grand_passed}/{grand_total} test cases passed")
    print("=" * 60)
    return 0 if grand_passed == grand_total else 1


if __name__ == "__main__":
    sys.exit(main())
