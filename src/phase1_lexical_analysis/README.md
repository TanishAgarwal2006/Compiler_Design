# Phase 1: Lexical Analysis (Lexer)

The Phase 1 Lexical Analyzer scans raw C source code text, strips whitespace and comments, processes escape sequences and numeric literal bases, and converts the input character stream into a structured token stream.

---

## 1. Components & Modules

- **`token_defs.py`**: Defines token specifications, keyword dictionaries, operator maps, and regular expression patterns.
- **`lexer.py`**: Core lexer engine implemented using **PLY (`ply.lex`)**. Manages lexer state transitions (`INITIAL`, `COMMENT`) and constructs token objects containing line numbers, token types, and lexeme values.
- **`run_lexer.py`**: Independent runner for Phase 1 lexical analysis supporting single-file tokenization and batch processing.

---

## 2. Lexical Specifications & Features

### Supported Token Types
- **Keywords:** `int`, `char`, `if`, `else`, `for`, `while`, `do`, `return`, `goto`, `break`, `continue`, `typedef`, `void`.
- **Identifiers:** Variable names, function names, labels, and typedef aliases (`[a-zA-Z_][a-zA-Z0-9_]*`).
- **Numeric Literals:**
  - Decimal: `123`, `0`
  - Hexadecimal: `0x1A`, `0XFF`
  - Octal: `075`, `010`
  - Binary: `0b1010`, `0B1101`
- **Character Literals:** Single quotes `'a'`, `'5'`, including escape sequences (`'\n'`, `'\t'`, `'\\'`, `'\''`, `'\"'`).
- **String Literals:** Double quotes `"hello world"`, `"result: %d\n"`.
- **Operators & Delimiters:** Arithmetic (`+`, `-`, `*`, `/`, `%`), Relational (`==`, `!=`, `<`, `<=`, `>`, `>=`), Logical (`&&`, `||`, `!`), Assignment (`=`, `+=`, `-=`, `*=`, `/=`, `%=`), Delimiters (`;`, `,`, `(`, `)`, `{`, `}`, `[`, `]`).

### Comment Handling
- **Single-Line Comments:** `// ...` skipped automatically.
- **Block Comments:** `/* ... */` handled using explicit lexer state transitions. Unterminated block comments trigger a lexical error.

---

## 3. Execution Commands

### Run Single File Lexical Analysis
```bash
python3 src/phase1_lexical_analysis/run_lexer.py tests/phase2_syntax/valid/02_if_else.c
# or using Makefile
make lex FILE=tests/phase2_syntax/valid/02_if_else.c
```

### Run Batch Lexical Analysis
```bash
# Phase 1 test cases only
make lex-phase1

# All project test cases
make lex-all
```

### Output to Log File
```bash
python3 src/phase1_lexical_analysis/run_lexer.py tests/phase2_syntax/valid/02_if_else.c --output tokens.txt
```
