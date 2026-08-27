# C-to-MIPS Compiler (Python / PLY)

A modular, four-phase compiler for a subset of the C programming language, implemented in **Python 3** using the **PLY (Python Lex-Yacc)** framework.

---

## 1. Overview & Compiler Phases

This project implements a multi-phase compiler pipeline converting high-level C source code into an Abstract Syntax Tree (AST), enriched symbol tables, and structured per-test logging, with scaffolding in place for Intermediate Code Generation and MIPS Target Codegen.

| Phase | Description | Output | Status |
|---|---|---|---|
| **Phase 1: Lexical Analysis** | Converts raw C source characters into a stream of typed tokens | Token Stream / Token Table | ✅ Implemented |
| **Phase 2: Syntax Analysis** | Parses token streams into a Context-Free Grammar AST and Symbol Table | Abstract Syntax Tree (AST) & Detailed Symbol Table | ✅ Implemented |
| **Phase 3: Intermediate Code Generation** | Lowering AST into Three-Address Code (TAC) quadruples | TAC Representation (`op`, `arg1`, `arg2`, `result`) | 🚧 Scaffolded (`src/phase3_intermediate_code/`) |
| **Phase 4: Optimization & Codegen** | Optimizing TAC (constant folding/propagation) and emitting MIPS assembly | MIPS Assembly (`.s`) | 🚧 Scaffolded (`src/phase4_optimization_codegen/`) |

---

## 2. Language Specifications & Supported Features

The compiler supports a representative subset of ANSI C:

* **Arithmetic & Logical Operators:** `+`, `-`, `*`, `/`, `%`, `++`, `--`, unary `-`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`, `=`, `+=`, `-=`, `*=`, `/=`, `%=`.
* **Control Flow Statements:** `if` / `else`, `for` loops, `while` loops, `do-while` loops.
* **Jumps & Labels:** `goto`, `break`, `continue`, user-defined labels (`label:`).
* **Data Types:** Primitive integer (`int`), character (`char`), and custom type aliases defined via `typedef`.
* **Arrays:** 1D arrays (`int arr[10]`) and Multi-dimensional arrays (`char matrix[5][10]`).
* **Functions & Call Semantics:** Function declarations, function definitions, direct function calls, and **recursive function calls**.
* **Standard I/O:** `printf` and `scanf` simulation.

---

## 3. Installation & Prerequisites

* **Python:** Python 3.10 or higher.
* **Dependencies:** `ply` (Python Lex-Yacc).

```bash
# Clone the repository
git clone https://github.com/TanishAgarwal2006/Compiler_Design.git
cd Compiler_Design

# Create and activate virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 4. Execution & Usage Guide

### 4.1 Master Test Suite & Log Generation
To run all 32 automated test cases across Phase 1 and Phase 2 and build clean per-case log files:

```bash
# Using Makefile
make run-all

# Or directly via bash script
./run.sh
```

### 4.2 Automated Test Runner (Pass/Fail Assertions)
To run automated test assertions across all test cases:

```bash
make test
# or
python3 tests/run_tests.py
```

### 4.3 Phase 1: Lexical Analysis Commands
Run lexical analysis independently:

```bash
# Run on a single file
make lex FILE=tests/phase2_syntax/valid/02_if_else.c
# or
python3 src/phase1_lexical_analysis/run_lexer.py tests/phase2_syntax/valid/02_if_else.c

# Run batch lexical analysis across all Phase 1 test cases
make lex-phase1

# Run batch lexical analysis across ALL test cases in the project
make lex-all
```

### 4.4 Phase 2: Syntax Analysis Commands
Run syntax analysis independently:

```bash
# Run on a single file
make parse FILE=tests/phase2_syntax/valid/02_if_else.c
# or
python3 src/phase2_syntax_analysis/run_parser.py tests/phase2_syntax/valid/02_if_else.c

# Run batch syntax analysis across Phase 2 test cases
make parse-phase2

# Run batch syntax analysis across ALL test cases
make parse-all
```

### 4.5 Unified Compiler Driver (`src/main.py`)
Run the full compiler pipeline on a single C source file:

```bash
# Run with default flags (Token table + Syntax status summary)
python3 src/main.py tests/phase2_syntax/valid/02_if_else.c

# Run with all detailed output flags (Tokens + AST + Detailed Symbol Table)
python3 src/main.py tests/phase2_syntax/valid/02_if_else.c --all
```

#### Supported CLI Flags (`src/main.py`)

| Flag | Description |
|---|---|
| `--tokens` | Displays the Phase 1 Token Table with enriched token roles |
| `--ast` | Displays the Phase 2 Abstract Syntax Tree (AST) structure |
| `--symbols` | Displays the Detailed Symbol Table (Identifier, Role, Type, Scope, Details) |
| `--ast-file <file>` | Appends the AST output to a custom log file |
| `--all` | Shorthand to print `--tokens`, `--symbols`, and `--ast` together |

---

## 5. Single Per-Test-Case Logging Architecture

When processing test files or batch runs, the compiler automatically generates **one clean, dedicated `.log` file per test case** inside `logs/`:

```text
logs/
├── phase1_lexical/
│   ├── valid/
│   │   ├── 01_arithmetic_operators.log
│   │   ├── 02_logical_and_relational_operators.log
│   │   └── ...
│   └── invalid/
│       ├── 01_illegal_character.log
│       └── ...
└── phase2_syntax/
    ├── valid/
    │   ├── 01_arithmetic_and_logical_operators.log
    │   ├── 02_if_else.log
    │   ├── 07_char_array.log
    │   ├── 11_recursive_function_call.log
    │   └── ...
    └── invalid/
        ├── 01_missing_semicolon.log
        └── ...
```

### Log File Contents (`<test_name>.log`)
Each log file consolidates all analysis artifacts for that specific file into a single document:
1. **Execution Status:** `[SUCCESS / PASSED]` or `[ERRORS DETECTED]`.
2. **Phase 1 Tokenization Output:** Enriched token table distinguishing function names, variables, parameters, arrays, typedefs, and labels.
3. **Phase 2 Detailed Symbol Table:** Comprehensive table showing scopes, types, signatures, and array dimensions.
4. **Phase 2 Abstract Syntax Tree:** Formatted tree hierarchy representing the program AST.

---

## 6. Detailed Identifier Role Classification

The compiler includes an AST-driven **Symbol Classifier** (`src/common/symbol_classifier.py`) that walks the syntax tree to resolve generic `IDENTIFIER` tokens into role-specific types:

| Identified Role | Token Representation | Description |
|---|---|---|
| `FUNCTION_NAME` | `FUNCTION_NAME` | Function names declared or invoked (e.g., `main`, `factorial`, `classify`) |
| `PARAMETER_NAME` | `PARAMETER_NAME` | Function parameter names in signatures and body scopes |
| `VARIABLE_NAME` | `VARIABLE_NAME` | Local or global scalar variables |
| `ARRAY_NAME` | `ARRAY_NAME` | 1D or multi-dimensional array identifiers |
| `TYPENAME` | `TYPENAME` | Types introduced via `typedef` statements |
| `LABEL_NAME` | `LABEL_NAME` | Target labels for `goto` control statements |
| `PRINTF` / `SCANF` | `PRINTF` / `SCANF` | Built-in standard library I/O function calls |

---

## 7. Repository Layout

```text
Compiler_Design/
├── src/
│   ├── main.py                    # Main Compiler Driver CLI
│   ├── phase1_lexical_analysis/
│   │   ├── lexer.py               # PLY Lexer engine & rules
│   │   ├── token_defs.py          # Token definitions, keywords, operator maps
│   │   ├── run_lexer.py           # Phase 1 standalone driver
│   │   └── README.md
│   ├── phase2_syntax_analysis/
│   │   ├── parser.py              # PLY LALR(1) Parser grammar rules
│   │   ├── ast_nodes.py           # AST Node data classes & formatter
│   │   ├── run_parser.py          # Phase 2 standalone driver
│   │   └── README.md
│   ├── phase3_intermediate_code/  # Phase 3 TAC generator scaffolding
│   │   └── README.md
│   ├── phase4_optimization_codegen/ # Phase 4 MIPS optimizer/emitter scaffolding
│   │   └── README.md
│   └── common/
│       ├── symbol_classifier.py   # Detailed Symbol Table builder & role classifier
│       ├── logger.py              # Log directory & file management utility
│       └── errors.py              # Centralized error reporting module
├── tests/
│   ├── phase1_lexical/valid/      # Phase 1 valid C test cases
│   ├── phase1_lexical/invalid/    # Phase 1 error handling test cases
│   ├── phase2_syntax/valid/       # Phase 2 feature test cases
│   ├── phase2_syntax/invalid/     # Phase 2 error handling test cases
│   └── run_tests.py               # Test suite execution harness
├── docs/
│   ├── ARCHITECTURE.md            # System architectural overview
│   ├── PROJECT_COMPILATION_REPORT.md # Technical implementation report
│   └── identifier_classification.md # Symbol classification technical design
├── makefile                        # Build & execution automation targets
├── run.sh                          # Master execution script
└── requirements.txt                # Python package requirements
```

---

## 8. Cleaning Build Artifacts

To remove all generated `logs/`, Python `__pycache__` directories, and temporary compilation files:

```bash
make clean
```
