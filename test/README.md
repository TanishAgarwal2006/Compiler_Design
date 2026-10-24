# Tests

Which test covers which feature: see [`COVERAGE.md`](COVERAGE.md) (also explains `tools/coverage_audit.py`).

Run everything: `make && ./run.sh bin/tacgen` (add `-q` to print failures only, `-k word` to run only cases whose path contains `word`).
The output is one line per case, `[PASS]` or `[FAIL]` plus the reason, then a table per group and a final `RESULT:` line.
The exit code is 0 only when everything passes.

## What a test case is

| Folder | A case is | It passes when |
| --- | --- | --- |
| `phase1_lexical/valid` | one `.c` file | the lexer accepts it (`bin/tacgen FILE --tokens`) |
| `phase1_lexical/invalid` | `name_buggy.c` (many marked bugs) + `name_buggy.err` | exit 1, every `:LINE: lexical error` line of the `.err` is reported, and no other error |
| `phase2_syntax/valid` | one `.c` file | the parser accepts it |
| `phase2_syntax/invalid` | `name_buggy.c` (one bug per `[n]` block) + `name_buggy.err` | exit 1, every `:LINE: syntax error` line of the `.err` is reported, and no other error. Blocks tagged `[accepted]`/`[boundary]` must give no error, `[stricter]` ones are rejected by this parser. Some blocks pin a second message caused by the `}` cascade |
| `phase3_tac/valid/<feature>` | `name.c` + `name.expected` (+ `name.args` for the command line, `name.in` for standard input) | it compiles, the IR runs in the interpreter and prints exactly `name.expected` |
| `phase3_tac/invalid/<feature>` | `<feature>_buggy.c` (one bug per function) + `.err` | exit code 1, no IR file written, every line of `name.err` appears in the messages, and no other error is printed |
| `unit/test_*.py` | small Python checks of one module each | no assertion fails |

Phase 3 valid features: `arithmetic`, `types`, `control_flow`, `arrays`, `strings`, `functions`, `input_output`, `declarations` (one big file each; `until`, `command_line`, `scanf_empty_input`, `strings_argv` are separate).
Phase 3 invalid: `arrays`, `control_flow`, `declarations`, `functions`, `input_output`, `types`, `unsupported` (`*_buggy.c`), plus `missing_main_buggy`, `bad_main_signature_buggy`, `unsupported_printf_value_buggy` (reported only when nothing else is wrong).
Unit test files: `test_literals` (escapes, character/string values), `test_semantic` (types, symbol table, annotations), `test_tac_basic` (IR for straight-line code, interpreter),
`test_control_flow`, `test_arrays`, `test_calls_io` (calls, recursion, scanf, argv),
`test_defensive` (internal "cannot happen" branches of the analyzer and generator), `test_ir_errors` (every IR interpreter error message),
`test_cli` (every command-line option and exit code), `test_syntax_messages` (end-of-file message, `;` hint, one report per bad statement).

## How the expected results were made
- Every `.expected` file was produced by compiling the same program with **gcc** (`gcc -w -fwrapv -include stdbool.h name.c`) and running it, so gcc is the judge.
  The programs avoid undefined behaviour (uninitialised variables, out-of-range indexes).
  The one exception is `until_loops`: `until` is not C, so its expected file is written by hand.
- `.err` files hold a short piece of each expected message, one per line.

## Adding a case
1. Valid: put `name.c` in a group folder, create `name.expected` with gcc as above (feed `name.in` on standard input and `name.args` on the command line if the program uses them).
2. Invalid: add a function with ONE deliberate mistake to the feature's `_buggy.c` and add a piece of the expected message in `name.err`.
   For a file with several mistakes write one piece per line (the number of lines must equal the number of errors).
3. Run `./run.sh bin/tacgen -k name`.
