#!/bin/bash
set -u

if [ -x "./venv/bin/python" ]; then
    DEFAULT_PYTHON="./venv/bin/python"
else
    DEFAULT_PYTHON="python3"
fi

PYTHON="${1:-$DEFAULT_PYTHON}"

echo "Running automated test suite (using $PYTHON)..."

"$PYTHON" tests/run_tests.py
STATUS=$?

echo ""
echo "Generating per-case log files under 'logs/'..."

rm -rf logs/
mkdir -p logs/

for file in tests/phase1_lexical/valid/*.c tests/phase1_lexical/invalid/*.c
do
    "$PYTHON" src/phase1_lexical_analysis/run_lexer.py "$file" > /dev/null 2>&1
done

for file in tests/phase2_syntax/valid/*.c tests/phase2_syntax/invalid/*.c
do
    "$PYTHON" src/main.py "$file" --all > /dev/null 2>&1
done

echo "Per-case single log files successfully generated in 'logs/':"
echo "  - logs/phase1_lexical/valid/<test_name>.log"
echo "  - logs/phase1_lexical/invalid/<test_name>.log"
echo "  - logs/phase2_syntax/valid/<test_name>.log"
echo "  - logs/phase2_syntax/invalid/<test_name>.log"

exit $STATUS

