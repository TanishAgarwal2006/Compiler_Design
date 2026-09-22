# Compiler Architecture & Phase Organization

This compiler project follows a modular, 4-phase design for processing C source code down to target assembly.

```
                  +-----------------------------------+
                  |          C Source Code            |
                  +-----------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| Phase 1: Lexical Analysis (src/phase1_lexical_analysis/run_lexer.py)    |
| - Scanning & Tokenization                                              |
| - Number base resolution (hex, octal, binary, dec)                      |
| - Comment & Literal processing                                         |
| - Output: Token Stream / Token Table                                   |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| Phase 2: Syntax Analysis & Symbol Table (src/phase2_syntax_analysis)  |
| - LALR(1) Parsing (parser.py)                                           |
| - Grammar verification                                                 |
| - AST Generation (ast_nodes.py)                                        |
| - Detailed Symbol Table Construction (src/common/symbol_classifier.py)  |
| - Output: Abstract Syntax Tree & Symbol Table                          |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| Phase 3: Intermediate Code Generation (src/phase3_intermediate_code)   |
| - Three-Address Code (TAC) generation                                  |
| - Temporary variable allocation                                        |
+------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
| Phase 4: Optimization & Codegen (src/phase4_optimization_codegen)       |
| - AST/TAC Optimization                                                 |
| - MIPS assembly emission                                               |
+------------------------------------------------------------------------+
```

## Data flow on a syntax error

Phase 2 doesn't just stop at the first mistake. `p_error` records the
offending token but leaves PLY in its default error-recovery state; two
grammar productions — `statement : error SEMI` and
`external_declaration : error SEMI` — give it a place to resynchronize.
PLY silently discards tokens (no further messages) until it reaches a `;`
it can shift, resumes parsing from there, and calls `errok()` in that
production's own action. Net effect: one real mistake is reported once,
and the parser keeps going to find any other real mistakes in the same
file, instead of drowning the output in an error for every token that
follows the first one.

## Running Phases Individually

### 1. Phase 1 (Lexical Analysis)
* Command: `python src/phase1_lexical_analysis/run_lexer.py <source.c>` or `make lex FILE=<source.c>`
* Directory: `src/phase1_lexical_analysis/`
* Purpose: Scans input source and generates a tokenization table, or reports lexical errors.

### 2. Phase 2 (Syntax Analysis & Symbol Table)
* Command: `python src/phase2_syntax_analysis/run_parser.py <source.c>` or `make parse FILE=<source.c>`
* Directory: `src/phase2_syntax_analysis/`
* Purpose: Parses the source against the LALR(1) grammar, builds the AST, and constructs a Detailed Symbol Table. On error, reports every genuine syntax mistake (via panic-mode recovery) rather than just the first.

### 3. Full Compiler Pipeline
* Command: `python src/main.py <source.c> --all` or `make run FILE=<source.c>`
* Script: `run.sh` (or `make run-all`) runs the automated test suite, then generates one per-case log file per test under `logs/<phase>/<category>/<test_name>.log`.

### 4. Phase 3 / Phase 4
* Not implemented yet. `src/phase3_intermediate_code/` and
  `src/phase4_optimization_codegen/` currently hold only a README each
  describing the intended TAC and MIPS-generation design; there is no
  code to run.

## Known scope boundaries

- No semantic analysis yet: a syntactically valid program can still
  reference undeclared names, mismatch types, or place `break`/`continue`
  outside a loop/switch. This is intentionally deferred, not overlooked —
  see `docs/PROJECT_COMPILATION_REPORT.md` for the full rationale.
- Reference declarators (`int &r = x;`), lambda functions, and dedicated
  file-I/O grammar are not implemented. See `tests/COVERAGE.md`'s "Known
  gaps" section.