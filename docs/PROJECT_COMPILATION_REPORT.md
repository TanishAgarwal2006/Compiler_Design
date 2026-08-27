# Compiler Design Project: Comprehensive Technical & Architectural Documentation

## 1. Project Overview & Objective

This project is a 4-phase **Toy C-to-MIPS Compiler** written in **Python** using the **PLY (Python Lex-Yacc)** framework.

- **Source Language:** A structured subset of ANSI C.
- **Target Language:** MIPS Assembly (Scaffolded for Phase 4).
- **Intermediate Representation (IR):** Three-Address Code (TAC) (Scaffolded for Phase 3).
- **Implementation Language:** Python 3.
- **Current Completion:** Phase 1 (Lexical Analysis) & Phase 2 (Syntax Analysis, AST Generation, Detailed Symbol Table Classification).

---

## 2. Language Subset & Scope Assumptions

To satisfy course specifications while remaining tractable for a toy compiler, specific design assumptions and scope boundaries were established:

### Included Language Features
1. **Control Flow:**
   - `if` / `else` conditional branches.
   - `for`, `while`, and `do-while` loops.
   - Jump statements: `goto`, `break`, `continue`.
2. **Data Types & Data Structures:**
   - Primitive Types: `int`, `char`.
   - Single-dimensional and Multi-dimensional arrays (e.g., `int arr[10]`, `char matrix[5][10]`).
   - Type definitions via `typedef` (e.g., `typedef int Integer;`).
3. **Functions & Input/Output:**
   - Function declarations and definitions with arguments.
   - Direct and recursive function calls (e.g., `factorial(n - 1)`).
   - Standard Library I/O simulation via `printf` and `scanf`.
4. **Expressions & Operators:**
   - Arithmetic: `+`, `-`, `*`, `/`, `%`, `++`, `--`, unary `-`.
   - Relational & Logical: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`.
   - Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`.

### Scope Exclusions & Architectural Rationale
- **Pointers & Pointer Declarators (`int *p`):** Excluded to simplify memory layout for MIPS stack management. Command-line-style input is implemented using `scanf()` into arrays rather than `char **argv`.
- **Structures & Unions (`struct`, `union`):** Excluded in favor of focus on multi-dimensional array layout.
- **Switch Statements (`switch`, `case`):** Excluded from the required spec. `switch` and `case` lex as generic identifiers to prevent keyword clutter.
- **Semantic Type-Checking:** Semantic type mismatch validation (e.g., assigning string to integer) is deferred to Phase 3 prior to TAC emission.

---

## 3. Detailed Component Architecture

### 3.1 Phase 1: Lexical Analysis (`src/phase1_lexical_analysis/`)
- **Module:** `lexer.py` & `token_defs.py`.
- **Mechanism:** Regular expression rules executed by `ply.lex`.
- **Key Implementation Highlights:**
  - **Numeric Bases:** Supports Decimal (`123`), Hexadecimal (`0x1A`), Octal (`075`), and Binary (`0b1010`) literal patterns.
  - **String & Character Literals:** Handles escape sequences (`\n`, `\t`, `\\`, `\'`, `\"`).
  - **Comment Stripping:** Supports single-line (`//`) and block comments (`/* ... */`) using lexer state transitions (`INITIAL` -> `COMMENT`).
  - **Multi-Character Rejection:** Validates that character constants contain exactly one character or valid escape sequence (rejects invalid constants like `'AB'`).

### 3.2 Phase 2: Syntax Analysis & AST (`src/phase2_syntax_analysis/`)
- **Module:** `parser.py` & `ast_nodes.py`.
- **Mechanism:** LALR(1) context-free grammar rules parsed via `ply.yacc`.
- **Key Implementation Highlights:**
  - **Operator Precedence:** Declared explicitly to eliminate shift/reduce conflicts for arithmetic and logical operators.
  - **Dangling-Else Resolution:** Resolved via PLY precedence rules (`nonassoc LOWER_THAN_ELSE`, `nonassoc ELSE`).
  - **AST Node Hierarchy:** AST is constructed using clean Python dataclasses (`Program`, `FunctionDef`, `IfStatement`, `ForStatement`, `FunctionCall`, `BinaryOp`, etc.) offering transparent inspection.

### 3.3 Context-Aware Symbol Classification (`src/common/symbol_classifier.py`)
- **Problem Statement:** In standard lexical analysis, a lexer cannot distinguish between a function name (`fib`), a variable (`r`), or a parameter (`n`) because lexers operate without grammar context.
- **Solution:** A post-parse AST traversal pass analyzes every identifier in the program and classifies its role:
  - `FUNCTION_NAME` (e.g., `main`, `classify`, `printf`)
  - `PARAMETER_NAME` (e.g., function formal parameters)
  - `VARIABLE_NAME` (e.g., local/global scalar variables)
  - `ARRAY_NAME` (e.g., 1D or multi-dimensional array identifiers)
  - `TYPENAME` (e.g., type aliases defined via `typedef`)
  - `LABEL_NAME` (e.g., `goto` target labels)
- **Output:** Generates a **Detailed Symbol Table** (`Identifier`, `Role`, `Type`, `Scope`, `Details`) and an **Enriched Token Table**.

### 3.4 Single Per-Test-Case Logging Architecture (`src/common/logger.py`)
- **Mechanism:** Every test file executed via `main.py`, `run_lexer.py`, `run_parser.py`, or `./run.sh` produces **exactly ONE clean `.log` file** under:
  `logs/<phase>/<category>/<test_name>.log`
- **Content of Each Single Log File:**
  1. **Header & Status:** `[SUCCESS / PASSED]` or `[ERRORS DETECTED]`.
  2. **Phase 1 Tokenization:** Enriched Token Table with role-specific token types.
  3. **Phase 2 Symbol Table:** Detailed Symbol Table mapping identifiers to roles, types, and scopes.
  4. **Phase 2 AST:** Complete Abstract Syntax Tree representation.

---

## 4. Key Engineering Fixes Implemented

1. **Lexer State Isolation:** Fixed state leakage where unterminated comments/strings in one test file corrupted subsequent test files. Each source file now receives a fresh lexer instance (`build_lexer()`).
2. **Multi-Character Literal Validation:** Prevented illegal multi-char literals like `'AB'` from lexing silently.
3. **Automated Test Harness (`tests/run_tests.py`):** Fixed path handling to run all 32 test cases automatically and report genuine PASS/FAIL verdicts.
4. **Clean-Up Utilities (`makefile`):** `make clean` recursively cleans `logs/`, `__pycache__`, and temporary build artifacts.

---

## 5. Verification Commands

- **Run Automated Test Suite (32 Test Cases):**
  ```bash
  make test
  ```

- **Run Full Pipeline & Generate All Log Files:**
  ```bash
  make run-all
  ```

- **Run a Single File:**
  ```bash
  make run FILE=tests/phase2_syntax/valid/02_if_else.c
  ```

- **Clean All Logs & Artifacts:**
  ```bash
  make clean
  ```
