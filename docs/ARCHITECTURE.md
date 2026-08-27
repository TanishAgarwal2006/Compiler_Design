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

## Running Phases Individually

### 1. Phase 1 (Lexical Analysis)
* Command: `python src/phase1_lexical_analysis/run_lexer.py <source.c>` or `make lex FILE=<source.c>`
* Directory: `src/phase1_lexical_analysis/`
* Purpose: Scans input C program and generates tokenization table.

### 2. Phase 2 (Syntax Analysis & Symbol Table)
* Command: `python src/phase2_syntax_analysis/run_parser.py <source.c>` or `make parse FILE=<source.c>`
* Directory: `src/phase2_syntax_analysis/`
* Purpose: Parses C program against LALR(1) grammar rules, builds the AST tree, and constructs a Detailed Symbol Table.

### 3. Full Compiler Pipeline
* Command: `python src/main.py <source.c> --all` or `make run FILE=<source.c>`
* Script: `run.sh` (or `make run-all`) runs all automated tests and generates per-case single log files in `logs/<phase>/<category>/<test_name>.log`.

