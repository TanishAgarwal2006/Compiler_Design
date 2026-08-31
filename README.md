# Toy C-to-MIPS Compiler

Course project for a small C compiler written in Python with
[PLY](https://www.dabeaz.com/ply/). The source language is a defined subset
of C. The eventual target is MIPS assembly, with three-address code (TAC) as
the intermediate representation.

## Current status

| Phase | Status | Output |
| --- | --- | --- |
| 1. Lexical analysis | Complete | Token table and lexical errors |
| 2. Syntax analysis | Complete | AST, identifier-role table, and syntax errors |
| 3. TAC generation | Not implemented | Planned |
| 4. Optimisation and MIPS generation | Not implemented | Planned |

The implemented C subset includes arithmetic, relational, logical, unary and
assignment operators; `if`/`else`; `for`, `while`, and `do`-`while`; integer
and character arrays (including multidimensional arrays); `printf` and
`scanf`; functions and recursion; `goto`, labels, `break`, and `continue`; and
`typedef`.

Pointers, `struct`, `union`, `switch`, floating-point types, and semantic type
checking are outside the current scope.

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
| Source language | Full C has a large grammar and many implementation-defined features. | The compiler accepts a documented C subset. This keeps the grammar small enough for a course project and gives the later TAC and MIPS phases a manageable target. |
| Compiler construction | Production compilers use separate lexical, syntactic, semantic, IR, optimisation, and code-generation stages. | The same staged architecture is used. Only lexical and syntax stages are implemented now; semantic analysis, TAC, optimisation, and MIPS are intentionally separate future work. |
| Identifier roles | In C, lexical tokens for user names are normally all identifiers; later stages resolve their meaning. | The lexer emits `IDENTIFIER` (or `TYPENAME` when a typedef is known). An AST walk later produces a readable role report. This avoids trying to guess meaning in the lexer. |
| Error checking | C compilers diagnose lexical, grammar, semantic, and linker errors in different stages. | Current errors are lexical and syntax errors only. A syntactically valid program can still use undeclared names, invalid types, or invalid `break`/`continue` placement until semantic analysis is added. |
| Intermediate and target languages | The requested compiler must eventually use TAC and MIPS. | TAC and MIPS are not emitted yet. The AST is kept explicit so it can be translated to TAC without reparsing source text. |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run the compiler

```bash
python3 src/main.py tests/phase2_syntax/valid/11_recursive_function_call.c --all
```

| Option | Output |
| --- | --- |
| no option | classified token table and parse result |
| `--tokens` | classified token table |
| `--symbols` | identifier role, type, scope, and details |
| `--ast` | formatted abstract syntax tree |
| `--ast-file FILE` | prints and appends the AST to `FILE` |
| `--all` | token table, symbol table, and AST |

Every single-file run also creates a report in `logs/`. Test files retain their
directory structure, for example
`logs/phase2_syntax/valid/11_recursive_function_call.log`.

## Tests and commands

```bash
make test                         # 32 automated lexical and syntax tests
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
  phase3_intermediate_code/      TAC phase placeholder
  phase4_optimization_codegen/   optimisation and MIPS phase placeholder
  common/                        errors, logging, symbol classification
tests/                           valid and invalid test programs
docs/                            architecture and project notes
```

`parsetab.py` and `parser.out` are generated by PLY. They are ignored by Git
and may be deleted at any time; PLY regenerates them when needed.
