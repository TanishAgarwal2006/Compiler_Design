#!/bin/bash
# Usage: ./run.sh [EXECUTABLE] [-k TEXT] [-q]     (default executable: bin/tacgen, built by `make`)
# Runs every test case under test/ through the executable and prints one report.
# Exit code is non-zero if any case fails.
cd "$(dirname "$0")"
EXE="${1:-bin/tacgen}"; [ $# -gt 0 ] && shift
[ -x "$EXE" ] || { echo "$EXE not found; run 'make' first"; exit 2; }
PY=python3; [ -x venv/bin/python ] && PY=venv/bin/python
exec $PY test/run_tests.py "$EXE" "$@"
