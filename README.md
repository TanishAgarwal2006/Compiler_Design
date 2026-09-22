# Toy C-to-MIPS Compiler

Course project for a small C compiler written in Python with
[PLY](https://www.dabeaz.com/ply/). The source language is a defined subset
of C (with a small C++-flavoured object extension). The eventual target is
MIPS assembly, with three-address code (TAC) as the intermediate
representation.

## Current status

| Phase | Status | Output |
| --- | --- | --- |
| 1. Lexical analysis | Complete | Token table and lexical errors |
| 2. Syntax analysis | Complete for the supported subset | AST, identifier-role table, and syntax errors |
| 3. TAC generation | Not started | Planned |
| 4. Optimisation and MIPS generation | Not started | Planned |

31/31 automated tests pass. The grammar builds with exactly one
shift/reduce conflict: a parenthesized-type-cast ambiguity around `RPAREN`
(`unary_expression : LPAREN type_specifier pointer_opt RPAREN
unary_expression`), resolved by PLY's default shift — this is the standard,
expected ambiguity for a C-style cast grammar. (Dangling-`else` is resolved
separately and cleanly via `nonassoc IFX`/`ELSE` precedence, so it never
shows up as a conflict at all.) Zero unused-token warnings.

The implemented C subset includes: arithmetic, relational, logical, bitwise,
unary and assignment (including compound bitwise) operators; the ternary
operator; `if`/`else`; `for`, `while`, `do`-`while`, `until`, and `do`-`until`;
`switch`/`case`/`default`; integer, character, and floating-point types
(`float`, `double`, plus `short`/`long`/`signed`/`unsigned` modifiers),
`bool`/`true`/`false`, `const`, `static`/`extern`; integer and character
arrays (including multidimensional arrays); `printf` and `scanf`; functions
(including variadic parameters `...`) and recursion; `goto`, labels, `break`,
and `continue`; `typedef`; pointers (including multi-level pointers and
function pointers) with `&`/`*`; `struct` and `union` with `.`/`->` member
access; `enum`; and a small C++-flavoured object subset: `class` with
`public`/`private`/`protected` access labels and inheritance (including
multiple base classes), scope resolution (`::`) for base-class/static member
access, and free-store `new`/`delete` (including the array forms `new T[n]`
/ `delete[] p`).

Syntax errors are reported using panic-mode recovery: after a genuine
mistake, the parser discards tokens up to the next `;` and resumes there,
instead of reporting an error for every token until end of file. See
`src/phase2_syntax_analysis/parser.py`'s `p_error`, `p_statement_error`, and
`p_external_declaration_error`.

**Known gaps** (see `tests/COVERAGE.md` for the full detail):
- **Reference declarators** (`int &r = x;`) — not implemented.
- **Lambda functions** — not implemented.
- **Dedicated file-I/O grammar** (`fopen`/`fread`/etc.) — no bespoke tokens
  or rules exist. `FILE *fp = fopen(...);`-shaped code happens to parse
  anyway, because `FILE` is pre-seeded as a known type name and `fopen` is
  just an ordinary function-call identifier — but there's no dedicated
  support or test for it.

Semantic type checking (e.g. verifying a pointer is only dereferenced where
one is expected, or that a `break` sits inside a loop/switch) is deferred to
a later phase; the parser accepts the grammar shown above but does not check
types or control-flow legality yet.

## Documentation map

| Document | What's in it |
| --- | --- |
| `README.md` (this file) | Status, feature list, setup, commands, layout |
| `src/phase1_lexical_analysis/README.md` | Lexer internals, token list, C-specific design decisions |
| `src/phase2_syntax_analysis/README.md` | Grammar internals, error recovery, C-specific design decisions |
| `docs/ARCHITECTURE.md` | Pipeline diagram, per-phase commands, data flow on error |
| `docs/PROJECT_COMPILATION_REPORT.md` | Full technical deep-dive: scope decisions, component architecture, engineering fixes made along the way |
| `tests/COVERAGE.md` | Every feature/error category mapped to the exact test file that exercises it |

## Implementation approach

The project is deliberately organised as a compiler pipeline rather than as a
single recogniser:

```text
C source -> PLY lexer -> token stream -> PLY LALR parser -> AST
                                                    -> identifier-role report
                                                    -> (future) TAC -> MIPS
```

Phase 1 is responsible only for forming tokens and reporting malformed
literals/comments. Phase 2 verifies grammar structure and builds an AST. The
identifier-role report is produced after parsing because a lexer cannot know
from the spelling of `sum` whether it is a variable, array, parameter, label,
or function. Type rules, scopes, and generated code belong to later phases.

## Project-wide design decisions

| Implementation choice | Standard C behaviour | Choice in this project and reason |
| --- | --- | --- |
| Source language | Full C has a large grammar and many implementation-defined features. | The compiler accepts a documented C subset (plus a small C++-flavoured object extension). This keeps the grammar manageable for a course project while still giving TAC/MIPS a realistic target. |
| Compiler construction | Production compilers use separate lexical, syntactic, semantic, IR, optimisation, and code-generation stages. | The same staged architecture is used. Only lexical and syntax stages are implemented now; semantic analysis, TAC, optimisation, and MIPS are intentionally separate future work. |
| Identifier roles | In C, lexical tokens for user names are normally all identifiers; later stages resolve their meaning. | The lexer emits `IDENTIFIER` (or `TYPENAME` when a typedef is known). An AST walk later produces a readable role report. This avoids trying to guess meaning in the lexer. |
| Error checking | C compilers diagnose lexical, grammar, semantic, and linker errors in different stages. | Current errors are lexical and syntax errors only, reported with panic-mode recovery so one mistake doesn't cascade. A syntactically valid program can still use undeclared names, invalid types, or invalid `break`/`continue` placement until semantic analysis is added. |
| Intermediate and target languages | The requested compiler must eventually use TAC and MIPS. | TAC and MIPS are not emitted yet. The AST is kept explicit so it can be translated to TAC without reparsing source text. |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run the compiler

```bash
python3 src/main.py tests/phase2_syntax/valid/functions_and_recursion.c --all
```

| Option | Output |
| --- | --- |
| no option | classified token table and parse result |
| `--tokens` | classified token table |
| `--symbols` | identifier role, type, scope, and details |
| `--ast` | formatted abstract syntax tree |
| `--ast-file FILE` | prints and appends the AST to `FILE` |
| `--all` | token table, symbol table, and AST |

Every single-file run also creates a report in `logs/`. Test files retain
their directory structure, for example
`logs/phase2_syntax/valid/functions_and_recursion.log`. The report format
(banner header, source path, status line, then either an error list or a
token table + symbol table + AST) is deliberately shaped to match the
logistics of a reference compiler project's per-test-case logs.

## Tests and commands

```bash
make test                         # 31 automated lexical and syntax tests
make run FILE=path/to/program.c   # complete Phase 1 + 2 output for one file
make lex FILE=path/to/program.c   # lexer only
make parse FILE=path/to/program.c # parser, AST, and symbol table
make run-all                      # test suite, then reports for all test files
make clean                        # remove generated files
```

`run.sh` accepts an optional Python interpreter as its first argument. It uses
`./venv/bin/python` when available, otherwise `python3`.

## Layout

```text
src/
  phase1_lexical_analysis/       lexer and standalone lexer runner
  phase2_syntax_analysis/        PLY grammar, AST nodes, parser runner
  phase3_intermediate_code/      TAC phase placeholder (not started)
  phase4_optimization_codegen/   optimisation and MIPS phase placeholder (not started)
  common/                        errors, logging, symbol classification
tests/                           valid and invalid test programs, COVERAGE.md
docs/                            ARCHITECTURE.md, PROJECT_COMPILATION_REPORT.md
logs/                            per-test-case generated reports (regenerated by run.sh/make run-all)
```

`parsetab.py` and `parser.out` are generated by PLY. They are ignored by Git
and may be deleted at any time; PLY regenerates them when needed.