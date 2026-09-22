# Compiler Design Project: Comprehensive Technical & Architectural Documentation

## 1. Project Overview & Objective

This project is a 4-phase **Toy C-to-MIPS Compiler** written in **Python**
using the **PLY (Python Lex-Yacc)** framework.

- **Source Language:** A structured subset of ANSI C, plus a small
  C++-flavoured object extension (`class`, access labels, inheritance,
  `new`/`delete`, `::`).
- **Target Language:** MIPS Assembly (not started; scaffolded for Phase 4).
- **Intermediate Representation (IR):** Three-Address Code (TAC) (not
  started; scaffolded for Phase 3).
- **Implementation Language:** Python 3.
- **Current Completion:** Phase 1 (Lexical Analysis) and Phase 2 (Syntax
  Analysis, AST Generation, Detailed Symbol Table Classification), both
  complete for the supported language subset. 31/31 automated tests pass.

---

## 2. Language Subset & Scope Assumptions

To satisfy course specifications while remaining tractable for a toy
compiler, specific design assumptions and scope boundaries were
established:

### Included Language Features
1. **Control Flow:**
   - `if` / `else` conditional branches, with dangling-`else` resolved to
     the nearest unmatched `if` via precedence declarations.
   - `for`, `while`, `do`-`while`, `until`, and `do`-`until` loops.
   - `switch` / `case` / `default`, including fall-through case labels.
   - Jump statements: `goto`, `break`, `continue`.
2. **Data Types & Data Structures:**
   - Primitive types: `int`, `char`, `float`, `double`, `bool`, `void`,
     plus `short`/`long`/`signed`/`unsigned` modifiers and `const`.
   - Single-dimensional and multi-dimensional arrays (e.g., `int arr[10]`,
     `char matrix[5][10]`).
   - Pointers, including multi-level pointers (`int **pp`) and function
     pointers (`int (*op)(int, int)`), with `&`/`*`.
   - `struct` and `union`, with `.`/`->` member access.
   - `enum`, with implicit or explicit constant values.
   - Type definitions via `typedef` (e.g., `typedef int Integer;`).
   - A small C++-flavoured object subset: `class` with
     `public`/`private`/`protected` access labels, inheritance (including
     multiple base classes), scope resolution (`::`) for base-class/static
     member access, and free-store `new`/`delete` (including array forms
     `new T[n]` / `delete[] p`).
3. **Functions & Input/Output:**
   - Function declarations and definitions with arguments, including
     variadic parameters (`...`).
   - Direct and recursive function calls (e.g., `factorial(n - 1)`).
   - Standard Library I/O simulation via `printf` and `scanf`.
   - `static` / `extern` storage classes.
4. **Expressions & Operators:**
   - Arithmetic: `+`, `-`, `*`, `/`, `%`, `++`, `--`, unary `-`/`+`.
   - Relational & Logical: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`.
   - Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`.
   - Ternary conditional: `?:` (including nesting).
   - Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`.
   - `sizeof` and explicit type casts.

### Scope Exclusions & Architectural Rationale
- **Semantic Type-Checking:** Semantic type mismatch validation (e.g.,
  assigning a string to an integer, verifying a pointer is only
  dereferenced where one is expected, or that `break`/`continue` sit
  inside a loop/switch) is deferred to a later phase, prior to TAC
  emission. The parser accepts the grammar shown above but does not check
  types or control-flow legality.
- **Preprocessor:** There is no macro-expanding preprocessor pass.
  `#include`/`#define`/etc. are recognized and consumed by the lexer (so
  standard-looking source still lexes cleanly) but have no effect;
  standard-header-based programs are not actually resolved against real
  headers.
- **No virtual dispatch:** The `class` subset accepts a comma-separated
  base list (`class C : public A, public B { ... }`) at the grammar level,
  but there is no virtual-function/vtable semantics behind it — it is a
  syntax-and-AST-level subset, not a full C++ object model.
- **Not implemented at all (see `tests/COVERAGE.md` for detail):**
  reference declarators (`int &r = x;`), lambda functions, and dedicated
  file-I/O grammar (`fopen`/`fread`/etc. — `FILE`-typed code happens to
  still parse because `FILE` is pre-seeded as a known type name, but there
  is no bespoke support or test for it).

---

## 3. Detailed Component Architecture

### 3.1 Phase 1: Lexical Analysis (`src/phase1_lexical_analysis/`)
- **Module:** `lexer.py` & `token_defs.py`.
- **Mechanism:** Regular expression rules executed by `ply.lex`.
- **Key Implementation Highlights:**
  - **Numeric Bases:** Supports Decimal (`123`), Hexadecimal (`0x1A`),
    Octal (`075`), and Binary (`0b1010`) integer literals, plus float
    literals (plain, exponent, and leading-dot forms).
  - **String & Character Literals:** Handles escape sequences (`\n`, `\t`,
    `\\`, `\'`, `\"`); rejects multi-character (`'AB'`) and empty (`''`)
    constants as lexical errors.
  - **Comment Stripping:** Supports single-line (`//`) and block comments
    (`/* ... */`) using lexer state transitions (`INITIAL` -> `COMMENT`).
  - **Lexer state isolation:** Each analysis gets a fresh lexer instance
    (`build_lexer()`), so an unterminated comment/string in one file can't
    corrupt the scan of the next one.

### 3.2 Phase 2: Syntax Analysis & AST (`src/phase2_syntax_analysis/`)
- **Module:** `parser.py` & `ast_nodes.py`.
- **Mechanism:** LALR(1) context-free grammar rules parsed via `ply.yacc`.
- **Key Implementation Highlights:**
  - **Operator Precedence:** Declared explicitly across assignment,
    ternary, logical, bitwise, relational, additive, multiplicative,
    unary, and postfix levels.
  - **Dangling-Else Resolution:** Resolved cleanly via PLY precedence
    rules (`nonassoc IFX`, `nonassoc ELSE`) — this does not itself produce
    a reported conflict.
  - **The one real grammar conflict:** PLY reports exactly one
    shift/reduce conflict, for `RPAREN` in the parenthesized type-cast
    production (`unary_expression : LPAREN type_specifier pointer_opt
    RPAREN unary_expression`), resolved by PLY's default shift. This is
    the standard, expected ambiguity for a C-style cast grammar and is
    unrelated to dangling-`else`.
  - **Panic-mode error recovery:** `p_error` records the offending token
    without calling `errok()` itself; `statement : error SEMI` and
    `external_declaration : error SEMI` give PLY a resynchronization
    point at the next `;`, so one real mistake is reported once instead
    of cascading into an error for every following token.
  - **AST Node Hierarchy:** Constructed using Python dataclasses
    (`Program`, `FunctionDefinition`, `IfStatement`, `ForStatement`,
    `SwitchStatement`, `StructSpecifier`, `ClassDeclaration`, `BinaryOp`,
    etc.) offering transparent inspection.

### 3.3 Context-Aware Symbol Classification (`src/common/symbol_classifier.py`)
- **Problem Statement:** In standard lexical analysis, a lexer cannot
  distinguish between a function name (`fib`), a variable (`r`), or a
  parameter (`n`) because lexers operate without grammar context.
- **Solution:** A post-parse AST traversal pass analyzes every identifier
  in the program and classifies its role:
  - `FUNCTION_NAME` (e.g., `main`, `classify`, `printf`)
  - `PARAMETER_NAME` (e.g., function formal parameters)
  - `VARIABLE_NAME` (e.g., local/global scalar variables)
  - `ARRAY_NAME` (e.g., 1D or multi-dimensional array identifiers)
  - `TYPENAME` (e.g., type aliases defined via `typedef`)
  - `LABEL_NAME` (e.g., `goto` target labels)
- **Output:** Generates a **Detailed Symbol Table**
  (`Identifier`, `Role`, `Type`, `Scope`, `Details`) and an **Enriched
  Token Table**.

### 3.4 Single Per-Test-Case Logging Architecture (`src/common/logger.py`)
- **Mechanism:** Every test file executed via `main.py`, `run_lexer.py`,
  `run_parser.py`, or `./run.sh` produces **exactly ONE clean `.log`
  file** under:
  `logs/<phase>/<category>/<test_name>.log`
- **Content of Each Single Log File:**
  1. **Header & Status:** `[SUCCESS / PASSED]` or `[ERRORS DETECTED]`.
  2. **Phase 1 Tokenization:** Enriched Token Table with role-specific
     token types (on success).
  3. **Phase 2 Symbol Table:** Detailed Symbol Table mapping identifiers
     to roles, types, and scopes (on success).
  4. **Phase 2 AST:** Complete Abstract Syntax Tree representation (on
     success).
  - Logistics deliberately mirror the shape of a reference compiler
    project's log output (banner header, source path, status line, token
    table, symbol table, AST) — see `README.md`'s "Run the compiler"
    section.

---

## 4. Key Engineering Fixes Implemented

1. **Lexer State Isolation:** Fixed state leakage where unterminated
   comments/strings in one test file corrupted subsequent test files.
   Each source file now receives a fresh lexer instance (`build_lexer()`).
2. **Multi-Character Literal Validation:** Prevented illegal multi-char
   literals like `'AB'` from lexing silently.
3. **Automated Test Harness (`tests/run_tests.py`):** Fixed path handling
   to run all test cases in `tests/` automatically and report genuine
   PASS/FAIL verdicts.
4. **Panic-Mode Error Recovery:** The parser originally had no
   resynchronization point after a syntax error — `p_error` called
   `errok()` immediately, which discarded only the single offending token
   and retried the very next one in the same broken parser state. This
   turned one real mistake into an error for nearly every token until end
   of file (observed cases: 10–13 reported errors for a single deliberate
   mistake). Fixed by adding `statement : error SEMI` and
   `external_declaration : error SEMI` productions and moving `errok()`
   into those productions' own actions, so PLY's built-in token-discarding
   does its job and the parser resynchronizes at the next `;`. Reduced
   every invalid test case to 1–2 reported errors, matching the intent of
   textbook panic-mode recovery.
5. **Test Suite Consolidation:** Reduced the test suite from ~47 files
   (largely one file per individual feature, with heavy overlap) to 31
   files organized by realistic scenario/theme (e.g. `control_flow.c`,
   `structs_unions_enums.c`), with `tests/COVERAGE.md` tracking exactly
   which file demonstrates which feature so nothing gets silently dropped.
6. **Clean-Up Utilities (`makefile`):** `make clean` recursively cleans
   `logs/`, `__pycache__`, `parsetab.py`, `parser.out`, and other
   generated artifacts.

---

## 5. Verification Commands

- **Run Automated Test Suite (31 Test Cases):**
```bash
  make test
```

- **Run Full Pipeline & Generate All Log Files:**
```bash
  make run-all
```

- **Run a Single File:**
```bash
  make run FILE=tests/phase2_syntax/valid/control_flow.c
```

- **Rebuild the Parse Table & Confirm the Conflict Count:**
```bash
  rm -f src/phase2_syntax_analysis/parsetab.py
  python3 -c "
  import sys; sys.path.insert(0,'src')
  import ply.yacc as yacc, phase2_syntax_analysis.parser as P
  yacc.yacc(module=P, start='program', tabmodule='dbg', outputdir='/tmp', debug=True)
  " 2>&1 | grep -i conflict
  # Expected: "WARNING: 1 shift/reduce conflict" (the cast-rule ambiguity)
```

- **Clean All Logs & Artifacts:**
```bash
  make clean
```