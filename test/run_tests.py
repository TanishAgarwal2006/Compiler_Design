#!/usr/bin/env python3
"""Run every test case through the compiler executable and print one report.

    python3 test/run_tests.py [EXECUTABLE] [-k TEXT] [-q]

    EXECUTABLE  the compiler (default bin/tacgen, built by `make`)
    -k TEXT     only run cases whose name contains TEXT
    -q          print failures and the summary only

Case layout (one big file per feature, details in test/README.md):
    phase1_lexical/valid/NAME.c             the lexer must accept it
    phase1_lexical/invalid/NAME_buggy.c     rejected; NAME_buggy.err lists ":LINE: lexical error" per bug
    phase2_syntax/valid/NAME.c              the parser must accept it
    phase2_syntax/invalid/NAME_buggy.c      rejected; NAME_buggy.err lists ":LINE: syntax error" per bug
    phase3_tac/valid/<feature>/NAME.c       compile, run the IR, compare with NAME.expected
        optional NAME.args (command line) and NAME.in (standard input)
    phase3_tac/invalid/<feature>/NAME_buggy.c   rejected; NAME_buggy.err has one expected
                                            error message fragment per line
    unit/test_*.py                          small checks of single modules
"""
import argparse
import importlib.util
import pathlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
IR_DIR = ROOT / "out" / "ir"
INTERPRETER = ROOT / "src" / "phase3_intermediate_code" / "tac_interpreter.py"
PY = str(ROOT / "venv" / "bin" / "python") if (ROOT / "venv" / "bin" / "python").exists() else sys.executable


def run(cmd, stdin=b"", timeout=120):
    return subprocess.run(cmd, input=stdin, capture_output=True, timeout=timeout, cwd=ROOT)


def compare_errors(path, err):
    """NAME.err holds one expected message fragment per line: every fragment must appear and nothing else may be reported."""
    wanted = [l for l in path.with_suffix(".err").read_text().splitlines() if l.strip()]
    for w in wanted:
        if w not in err:
            return f"missing expected message {w!r}"
    got = len(re.findall(r"^.+:(?:\d+|\?): \w+ error: ", err, re.M))
    if got != len(wanted):
        return f"expected {len(wanted)} error(s), got {got}"


def check_reject(exe, path, kinds):
    r = run([exe, str(path)] + (["--tokens"] if "phase1" in str(path) else []))
    err = r.stderr.decode()
    if r.returncode != 1:
        return f"expected exit code 1, got {r.returncode}"
    if not any(f"{k} error" in err for k in kinds):
        return f"expected a {'/'.join(kinds)} error, got: {err.strip()[:100]}"
    return compare_errors(path, err)


def check_accept(exe, path, kinds):
    r = run([exe, str(path)] + (["--tokens"] if "phase1" in str(path) else []))
    if r.returncode != 0:
        return f"compiler rejected it: {r.stderr.decode().strip()[:150]}"


def check_valid_phase3(exe, path, kinds):
    ir = IR_DIR / path.relative_to(HERE / "phase3_tac" / "valid").with_suffix(".ir")
    r = run([exe, str(path), "-o", str(ir)])
    if r.returncode != 0:
        return f"compile failed: {r.stderr.decode().strip()[:150]}"
    args = path.with_suffix(".args").read_text().split() if path.with_suffix(".args").exists() else []
    stdin = path.with_suffix(".in").read_bytes() if path.with_suffix(".in").exists() else b""
    out = run([PY, str(INTERPRETER), str(ir)] + args, stdin)
    want = path.with_suffix(".expected").read_bytes()
    if out.stdout != want:
        got, exp = out.stdout.decode(errors="replace").splitlines(), want.decode(errors="replace").splitlines()
        for n, (g, e) in enumerate(zip(got + [""] * len(exp), exp + [""] * len(got)), 1):
            if g != e:
                return f"output differs at line {n}: got {g!r}, expected {e!r}"
        return "output differs"


def check_invalid_phase3(exe, path, kinds):
    ir = IR_DIR / "rejected" / (path.stem + ".ir")
    ir.unlink(missing_ok=True)
    r = run([exe, str(path), "-o", str(ir)])
    err = r.stderr.decode()
    if r.returncode != 1:
        return f"expected exit code 1, got {r.returncode}"
    if ir.exists():
        return "an IR file was written despite the error"
    return compare_errors(path, err)


GROUPS = [  # (label, folder, check, error kinds)
    ("phase1 lexical valid", "phase1_lexical/valid", check_accept, ()),
    ("phase1 lexical invalid", "phase1_lexical/invalid", check_reject, ("lexical",)),
    ("phase2 syntax valid", "phase2_syntax/valid", check_accept, ()),
    ("phase2 syntax invalid", "phase2_syntax/invalid", check_reject, ("lexical", "syntax")),
    ("phase3 compile+run valid", "phase3_tac/valid", check_valid_phase3, ()),
    ("phase3 semantic invalid", "phase3_tac/invalid", check_invalid_phase3, ()),
]


def run_unit_tests(verbose):
    sys.path.insert(0, str(ROOT / "src"))
    results = []
    for path in sorted((HERE / "unit").glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in sorted(n for n in dir(module) if n.startswith("test_")):
            try:
                getattr(module, name)()
                results.append((f"unit/{path.stem}::{name}", None))
            except Exception as exc:  # report any failure and keep going
                results.append((f"unit/{path.stem}::{name}", repr(exc)))
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exe", nargs="?", default="bin/tacgen")
    ap.add_argument("-k", default="")
    ap.add_argument("-q", action="store_true")
    a = ap.parse_args()
    exe = str((ROOT / a.exe) if not pathlib.Path(a.exe).is_absolute() else a.exe)
    if not pathlib.Path(exe).exists():
        sys.exit(f"{a.exe} not found; run 'make' first")

    summary = []
    failed = 0
    for label, folder, check, kinds in GROUPS:
        files = sorted(p for p in (HERE / folder).rglob("*.c") if a.k in str(p))
        with ThreadPoolExecutor(8) as pool:
            reasons = list(pool.map(lambda p: check(exe, p, kinds), files))
        print(f"== {label.strip()}  ({folder})")
        for p, why in zip(files, reasons):
            if why or not a.q:
                print(f"  [{'FAIL' if why else 'PASS'}] {p.relative_to(HERE / folder)}" + (f"\n         {why}" if why else ""))
        bad = sum(1 for w in reasons if w)
        summary.append((label.strip(), len(files) - bad, len(files)))
        failed += bad

    unit = [r for r in run_unit_tests(a.q) if a.k in r[0]]
    print("== unit tests  (test/unit)")
    for name, why in unit:
        if why or not a.q:
            print(f"  [{'FAIL' if why else 'PASS'}] {name}" + (f"\n         {why}" if why else ""))
    bad = sum(1 for _, w in unit if w)
    summary.append(("unit tests", len(unit) - bad, len(unit)))
    failed += bad

    print("\n" + "-" * 52)
    print(f"{'GROUP':<32}{'PASSED':>8}{'FAILED':>8}{'TOTAL':>6}")
    for label, ok, total in summary:
        print(f"{label:<32}{ok:>8}{total - ok:>8}{total:>6}")
    total = sum(t for _, _, t in summary)
    print("-" * 52)
    print(f"{'ALL':<32}{total - failed:>8}{failed:>8}{total:>6}")
    print("RESULT: " + ("ALL TESTS PASSED" if not failed else f"{failed} TEST(S) FAILED"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
