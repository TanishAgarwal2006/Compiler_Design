# Toy C Compiler (Phases 1 to 3): C subset -> three-address code

A compiler written in Python (with the PLY library) for a small subset of C. It reads a C file and writes an
**IR file** of *three-address code* (TAC): a list of very simple instructions, one operation per line, such as `t3 = t1 + t2`.
A small interpreter is included so you can run the IR file and check the compiler. Turning the IR into MIPS is Phase 4 and is **not** part of this project yet.

| Phase | Job | Folder | Status |
| --- | --- | --- | --- |
| 1 Lexical analysis | cut the text into tokens, report bad characters | `src/phase1_lexical_analysis/` | done |
| 2 Syntax analysis | check the grammar, build the program tree (AST) | `src/phase2_syntax_analysis/` | done |
| 3 Semantic analysis + IR | check names and types, write the IR file, run it | `src/phase3_intermediate_code/` | done |
| 4 Optimisation + MIPS | | `src/phase4_optimization_codegen/` | not started |

```
prog.c --lexer--> tokens --parser--> tree --semantic analyzer--> checked tree + symbol table --IR generator--> prog.ir
prog.ir --tac_interpreter.py--> program output (used to test the compiler)
```

## 1. Install and run

You need Python 3.10 or newer. The only extra package is PLY (listed in `requirements.txt`).

```
pip install -r requirements.txt      # or: make setup   (creates ./venv and installs PLY there)
make                                 # creates the launcher bin/tacgen
bin/tacgen prog.c -o prog.ir         # compile to an IR file
python3 src/phase3_intermediate_code/tac_interpreter.py prog.ir [args] < input.txt   # run the IR
./run.sh bin/tacgen                  # run every test (add -q to show failures only)
```

Look at one stage only (all go to the screen, nothing is written):

| Command | Shows |
| --- | --- |
| `bin/tacgen prog.c --tokens` | Phase 1 only: the token table |
| `bin/tacgen prog.c` | Phases 1 and 2: reports `Syntax analysis: OK` or the errors |
| `bin/tacgen prog.c --ast` | the program tree |
| `bin/tacgen prog.c --symbols` | tokens with names labelled (function, variable, array...) and the symbol report |
| `bin/tacgen prog.c --semantic` | the scoped symbol table with sizes and frame offsets |
| `bin/tacgen prog.c --tac` | the IR printed on the screen |
| `bin/tacgen prog.c --all` | tokens, symbol report and tree |

One log file per test case (token table, symbols, tree, symbol table with offsets, IR, program output): `make log1`, `make log2`, `make log3`, `make logall`, or `make logcase FILE=test/.../x.c`; written under `out/logs/` (see `tools/mklog.sh`).

Exit code is `0` when the program is fine and `1` when it has an error. No IR file is written for a bad program.

## 2. What the compiler supports

- **Types:** `int` (4 bytes), `char` (1 byte, signed), `float` (4 bytes, single precision; `double` means the same), `bool` with `true`/`false`
  (a value stored in a `bool` becomes 0 or 1). `short`, `long`, `signed`, `unsigned` behave exactly like `int` (32-bit).
- **Operators:** `+ - * / %`, comparisons, `&& || !`, `& | ^ ~ << >>`, `?:`, comma, `=`, all compound assignments (`+=` ...), `++`, `--`, casts, `sizeof`.
- **Statements:** `if/else`, `for` (also `for (int i = 0; ...)`), `while`, `do-while`, `until`, `do-until`, `switch/case/default`, `break`, `continue`, `goto` and labels, `return`.
- **Arrays:** `int`, `char`, `float` arrays with 1 to 3 dimensions, initialiser lists, global arrays, string initialisers, array parameters.
- **Strings:** string literals, `char *` variables and `char s[]`, `argv[i]`, `atoi`, `%s`. Indexing works; there is no pointer arithmetic.
- **Functions:** parameters, return values, prototypes, recursion, mutual recursion, `main()`, `main(void)`, `main(int argc, char *argv[])`.
- **Input/output:** `printf` and `scanf` with `%d %i %c %f %s %%` (no width or precision). `scanf` returns how many values it read (-1 at end of input) and leaves a variable unchanged when the text does not match, so `while (scanf("%d", &x) == 1)` works.
- **Declarations:** global variables with constant values, `typedef` (the new type name can be used right after its declaration, in the very next declaration), `enum`, `const`, `extern` + later definition, `static` globals/functions, nested scopes with shadowing.
- **Parsed but rejected in Phase 3** (error `unsupported feature: ...`): pointers other than `char *`, `&` outside `scanf`, `struct`, `union`, classes
  (constructors, `Class::method`, `this`), `new`/`delete`, lambdas, `auto`, references, function pointers, variadic functions, `static` local variables,
  `malloc`/`free`, file I/O (`fopen` ...).

## 3. What an error looks like

Every error has the same layout, whichever phase finds it. All errors of a file are collected and printed together, sorted by line:

```
prog.c:3: syntax error: unexpected token 'return' (is a ';' missing at the end of line 3?)
     3 |     int x = 5
1 error found. No output was produced.
```
Lexical errors stop the compiler before Phase 2; syntax errors stop it before Phase 3 (the tree would be incomplete).

## 4. Folder map

| Path | Purpose |
| --- | --- |
| `src/main.py` | the command-line driver that runs the phases (options in the table above) |
| `src/phase1_lexical_analysis/` | `lexer.py` token rules, `token_defs.py` keyword and token names; own README |
| `src/phase2_syntax_analysis/` | `parser.py` grammar, `ast_nodes.py` tree classes; own README |
| `src/phase3_intermediate_code/` | type system, symbol table, semantic analyzer, TAC generator, IR interpreter; own README with the IR format |
| `src/phase4_optimization_codegen/` | placeholder with the plan for Phase 4 |
| `src/common/` | error lists and the one error printer, literal helpers (character/string escapes), a report-only symbol labeller |
| `test/` | all test programs, the test runner, unit tests; see `test/README.md` |
| `tools/` | `coverage_audit.py` (is every token, keyword, tree node and error message tested?), `genfuzz.py` + `difftest.py` (random programs compared with gcc), `mklog.sh` (one log file per test case) |
| `makefile`, `run.sh` | `make` builds `bin/tacgen`; `run.sh` runs every test with it |
| `requirements.txt` | PLY (3.11 or newer) |

## 5. Known limits (on purpose, to keep the compiler simple)
- `short`, `long`, `unsigned` are 32-bit `int`; `double` is a 32-bit `float` (`sizeof(double)` is 4). A float result can differ from gcc in the last digit when a non-exact double literal such as `0.1` is mixed in.
- `scanf("%i")` reads a decimal number like `%d` (no `0x` or leading-0 octal input).
- One row of a 2-D array cannot be passed to a function (`f(m[1])`); whole arrays can.
- Array indexes are not range-checked (undefined in C as well).
- `case`/`default` outside a `switch` is a syntax error. Names must be declared before use (prototypes are fine).
- `printf` cannot be used as a value.
