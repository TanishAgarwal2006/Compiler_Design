# Phase 1: Lexical Analyzer



## 1. Build and Run Instructions

This project uses Python and PLY (Python Lex-Yacc). The repository provides a makefile (named `makefile`) and a `run.sh` script to run all test cases in the `test/` directory.

Required runtime/dependencies:
- Python 3
- PLY 

Installation / environment notes (what the repository expects)
- The repository expects a virtual environment named `venv` at the project root 
- PLY must be available in that Python environment.

## How to Execute the Lexer

### Clean Previous Outputs

```bash
make clean
```

Removes previously generated output files.

### Run Lexer Test Cases

```bash
./run
```

The script runs the lexer on all `.c` files inside the `test/` directory and stores the complete output of all test cases in:

```text
output.txt
```

The output file contains:

- Generated token tables for valid test cases.
- Lexical error messages for invalid test cases.




---

# 2. Design Decisions and C-Specific Implementation Choices

This section explains deviations, simplifications, and key implementation decisions made when building a C-subset lexer for this project.


| Implementation Choice | Actual C Implementation | Why We Did So |
|---|---|---|
| `printf`, `scanf`, and `sizeof` are included in the reserved token list | In standard C, `printf` and `scanf` are library functions, not language keywords. They are normally treated as identifiers and resolved through the symbol table. `sizeof`, however, is a C keyword/operator. | Our compiler specification requires handling `printf` and `scanf` as predefined constructs, so they are included as reserved tokens for simpler lexical and parsing support. `sizeof` is included because it has special syntactic behavior in C. |
| Multi-character character constants like `'AB'` are not treated as lexical errors | In C, multi-character constants are valid lexical constructs (e.g., `'AB'`). Their value is implementation-defined and depends on the compiler. | Since `'AB'` is a valid character constant from a lexical perspective, the lexer only recognizes it as a `CHAR_CONSTANT`. Any restrictions regarding length or usage can be handled later during semantic analysis. This keeps lexical analysis focused on token formation rather than meaning. |
| Numeric literals beginning with `0` may have binary/octal/hexadecimal interpretation issues | C supports octal (`0123`) and hexadecimal (`0x123`) literals. Binary literals (`0b1010`) are not part of standard C but are supported by some compilers as extensions. Invalid forms such as `09` create ambiguity because octal digits only allow `0-7`. | We support hexadecimal, binary, and octal formats according to the compiler requirements. Validation of some edge cases involving numeric formats is handled carefully at the lexical level, while further numeric interpretation can be handled in later compiler stages if required. |
| Invalid numeric-identifier combinations like `123abc` are not treated as lexical errors currently | In C, tokens cannot generally be merged without proper separation. A sequence like `123abc` is not a valid identifier or numeric constant. | We currently allow the lexer to tokenize such cases into separate tokens (`INTEGER_CONSTANT` followed by `IDENTIFIER`) and defer handling to later stages. This keeps the lexer simpler, while syntactic validation can determine whether such token sequences form an invalid construct. |


---

# 3. Lexer Architecture and General Working

What lexical analysis does in this pipeline
- The lexer converts source text into a stream of tokens (lexemes paired with token types and values). This token stream is the input for the parser (syntax analysis) in later phases.

Why PLY was chosen
- PLY provides a Python implementation of lex/yacc with a familiar rule-based design: token regexes, token action functions, and lexer states.
- It integrates cleanly with Python and supports exclusive lexer states, which the implementation uses for multi-line constructs (comments, strings, char literals).

How PLY lexing works in this implementation
- Token definitions: tokens are declared in `src/utils/token.py` (the `tokens` list) and `reserved` maps keywords to token names.
- Regular expressions: token recognition is implemented via PLY by defining either:
  - module-level variables like `t_PLUS = r'\+'` (simple tokens), or
  - functions whose docstring or regex decorator is the pattern (complex rules such as numbers, identifiers, and exclusive-state start/end rules).
- Token functions: functions like `t_IDENTIFIER`, `t_INTEGER_HEX`, `t_begin_STRING`, etc. perform additional processing (e.g., type conversion, setting `t.type`).
- Returning tokens: functions that produce tokens return `t`. For example, `t_INTEGER_DEC` converts the lexeme to an int and sets `t.type = 'INTEGER_CONSTANT'` then `return t`.
- Ignored characters: `t_ignore = ' \t'` in the INITIAL state disables spaces/tabs. Each exclusive state defines its own ignore rules (e.g., `t_COMMENT_ignore = ' \t'`).
- Error handling: `t_error` in INITIAL and state-specific `t_*_error` callbacks handle illegal characters or state-local problems and call `add_lex_error()` where appropriate.

Interaction between files
- `lexer.py`: holds the PLY lexer rules, states, regexes, and the `lexer` object (`lexer = lex.lex()`).
- `token.py`: defines the `tokens` list and `reserved` dictionary. The lexer relies on the token list and reserved mapping; PLY imports `tokens` from `utils.token`.
- `errors.py`: `add_lex_error()` stores lexical errors in a global list `lex_errors`. `main.py` prints these after tokenization.
- `main.py`: initializes/reset lexer state, feeds input to the lexer (`lexer.input(code)`), iterates `lexer.token()` to receive tokens, and presents output or errors.

How tokens are declared and generated
- Simple tokens are provided as module-level variables (e.g., `t_PLUS = r'\+'`). These map straight lexemes to token types defined in `utils/token.py`.
- Complex tokens are functions:
  - Numeric formats (hex, bin, oct, decimal) have dedicated functions, convert to Python ints, and set `t.type = 'INTEGER_CONSTANT'`.
  - Identifiers use `t_IDENTIFIER` with regex `[a-zA-Z_][a-zA-Z0-9_]*`. After recognition, the implementation checks the `reserved` mapping to convert certain lexemes to keyword token types (e.g., `'if'` → `'IF'`).
  - The "lexer hack" for `typedef`: if `lexer.typedefs` exists and the identifier value is in that set, its token type is changed to `TYPENAME` before returning the token.
- Token stream production:
  Source text → lexer.input(text) → repeated calls to lexer.token() → tokens returned until EOF (token() returns None).

Overall flow
Source Code → Lexer → Tokens → Parser

---

# 4. Comments Handling

Comments are handled in two forms: single-line (`//`) and multi-line (`/* ... */`). Multi-line comments use an exclusive lexer state to properly handle nested lines, newlines, and unterminated comments.

## Single Line Comments
- Rule implemented:

```python
def t_LINE_COMMENT(t):
    r'//.*'
    pass
```

- Regex: `//.*` matches '//' followed by any characters until the end of the line.
- Behavior:
  - The rule's function body is `pass`, so single-line comments are ignored and produce no tokens.
  - Newlines are handled by the general `t_newline` rule (so the line number is incremented when a newline occurs).

## Multi-Line Comments
- An exclusive state `COMMENT` is used: `states = (("COMMENT","exclusive"), ...)`
- Why an exclusive state:
  - Block comments can contain newlines and arbitrary characters including `*` and `/` pairs. Using an exclusive state isolates the comment scanning logic, avoids accidental token emission inside comments, and allows precise newline counting and proper handling of unterminated comments.

```

- Handling unterminated block comments:

```python
def t_COMMENT_eof(t):
    add_lex_error(f"Unterminated block comment starting at line {t.lexer.comment_start}")
```

- Other state rules:
  - `t_COMMENT_ignore = ' \t'` ensures spaces and tabs inside block comments are skipped automatically by PLY.
  - `def t_COMMENT_error(t): t.lexer.skip(1)` silently skips other weird characters inside comment.

Important notes
- Block comments produce no tokens; they are completely skipped from the token stream.
- Unterminated block comments are recorded via `add_lex_error()` so the rest of the compilation pipeline can report them.


---


# 5. String Literal Handling

Strings are handled using an exclusive `STRING` lexer state to correctly process string contents, escapes, spaces, and detect unterminated strings.

## Why a separate STRING state?

- String contents may contain characters like spaces, operators, and symbols that could otherwise match other token rules.
- The exclusive state ensures that all characters are processed as part of the string until the closing `"` is encountered.

## STRING State Implementation

### Entering STRING state

```python
def t_begin_STRING(t):
    r'\"'
    t.lexer.string_start = t.lexer.lineno
    t.lexer.string_buf = '"'
    t.lexer.begin('STRING')
```

When `"` is encountered, the lexer enters STRING mode and starts collecting the string contents.

### Capturing string contents

```python
def t_STRING_char(t):
    r'([^"\n\\]|\\.)+'
    t.lexer.string_buf += t.value
```

The regex captures:

- Normal characters except `"`, newline, and `\`
- Escape sequences (`\` followed by any character)

### Closing the string

```python
def t_STRING_end(t):
    r'\"'
    t.lexer.string_buf += '"'
    t.value = t.lexer.string_buf
    t.type = 'STRING_LITERAL'
    t.lexer.begin('INITIAL')
    return t
```

Once the closing quote is found, the complete lexeme is returned as a `STRING_LITERAL` token.

### Error Handling

Unterminated strings crossing a newline, strings reaching EOF without a closing quote, and unexpected characters are detected through:

```python
def t_STRING_newline(t):
    r'\n'
def t_STRING_eof(t):
def t_STRING_error(t):
```


---

# 6. Character Literal Handling

Character constants are processed using a separate exclusive `CHAR` state, similar to strings, to handle single quotes, escape sequences, and malformed character literals.

## Why CHAR state?

- Character literals require tracking from opening `'` to closing `'`.
- The state helps detect errors such as empty constants and unterminated characters while keeping character processing isolated.

## CHAR State Implementation

### Entering CHAR state

```python
def t_begin_CHAR(t):
    r"'"
    t.lexer.char_start = t.lexer.lineno
    t.lexer.char_buf = "'"
    t.lexer.begin('CHAR')
```

### Capturing content

```python
def t_CHAR_content(t):
    r"([^'\\\n]|\\.)+"
    t.lexer.char_buf += t.value
```

Accepts normal characters and escape sequences.

### Closing character

```python
def t_CHAR_end(t):
    r"'"
```

Returns a `CHAR_CONSTANT` token after the closing quote. Empty character constants (`''`) are detected and reported as lexical errors.

## Error Handling

The lexer detects:

- Unterminated characters due to newline:
- Unterminated characters due to EOF:
- Unexpected characters, via these functions

```python
def t_CHAR_newline(t):
    r'\n'
def t_CHAR_eof(t):
def t_CHAR_error(t):
```

## Deferred Semantic Checks

The lexer only identifies the character literal boundary. The following are handled later:

- Multi-character constants such as `'AB'`
- Detailed escape-sequence validation

Using a separate CHAR state provides accurate error reporting and keeps character tokenization separate from string processing.


---

# 7. Integer Literal Handling

The lexer supports multiple integer literal formats and performs base detection during lexical analysis.

- **Decimal Integers**
  - Standard base-10 integers are supported.
  - Examples: 0, 10, 12345
  - These are converted into integer values and returned as `INTEGER_CONSTANT` tokens.

- **Hexadecimal Integers**
  - Hexadecimal literals using the `0x` or `0X` prefix are supported.
  - Examples: 0x123, 0XABC
  - Hexadecimal digits (`0-9`, `a-f`, `A-F`) are recognized and converted into integer values.

- **Binary Integers**
  - Binary literals using the `0b` or `0B` prefix are supported.
  - Examples: 0b1010, 0B1111
  - Only binary digits (`0` and `1`) are accepted after the prefix.

- **Octal Integers**
  - Octal literals beginning with `0` are supported.
  - Examples: 0123, 077
  - Digits are restricted to the octal range (`0-7`).

- **Integer Rule Ordering**
  - The lexer checks prefixed formats (hexadecimal, binary, and octal) before decimal numbers.
  - This ensures literals such as 0x123, 0b1010, and 0123 are correctly identified instead of being split into incorrect decimal tokens.

- **Invalid Octal Detection**
  - The lexer detects malformed octal literals containing digits `8` or `9`.
  - Examples: 09, 078
  - These are reported as lexical errors instead of being incorrectly tokenized as separate numbers.

## Edge Cases Handled

- `0` is treated as a valid integer literal.
- Numbers with `0x`/`0X` prefixes are interpreted as hexadecimal.
- Numbers with `0b`/`0B` prefixes are interpreted as binary.
- Leading-zero numbers such as `0123` are interpreted as octal.
- Invalid octal forms such as `09` and `078` are rejected during lexical analysis.
- Numeric values are converted into integer form before being passed to later compiler phases.

The lexer focuses on identifying valid integer literal formats, while deeper checks such as range limitations are handled in later compiler stages.


---


# 8. Identifier Handling

Identifier regex and behavior
- Rule:

```python
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
```

- Regex explanation:
  - The first character must be an ASCII letter or underscore: `[a-zA-Z_]`.
  - Subsequent characters may be letters, digits, or underscores: `[a-zA-Z0-9_]*`.
  - This supports standard C-style identifiers including leading underscores.

Allowed characters and examples
- Valid examples recognized by the lexer:
  - `variable`
  - `variable123`
  - `_counter`
  - `_` (single underscore is accepted)
- Identifiers beginning with digits are not matched (they will match numeric token rules instead).

Interaction with reserved keywords
- After matching an identifier, the lexer checks:

```python
t.type = reserved.get(t.value, 'IDENTIFIER')
```

- If the lexeme appears in `reserved` (defined in `src/utils/token.py`), its token type is replaced by the appropriate keyword token (for example `if` → `IF`).

Typedef "lexer hack"
- After reserved lookup, the lexer additionally checks for typedef-registered names:

```python
if t.type == 'IDENTIFIER':
    if hasattr(t.lexer, 'typedefs') and t.value in t.lexer.typedefs:
        t.type = 'TYPENAME'
```

- Explanation:
  - The lexer supports a dynamic set `lexer.typedefs` (not populated in the lexical phase by default in this code) that a parser could populate when encountering a `typedef`. When present, identifiers that match names in this set are emitted as `TYPENAME`. This is a pragmatic approach to help the parser disambiguate type names from identifiers without complex grammar rules.



---

# 9. Reserved Keywords

The reserved keyword mechanism:
- `src/utils/token.py` defines `reserved` as a dictionary mapping lowercase lexemes to their token names. The lexer consults this dictionary on every identifier match and returns the mapped token type when appropriate.

Supported keywords (as defined in token.py)
- Control flow:
  - `if`  → `IF`
  - `else` → `ELSE`
  - `for`  → `FOR`
  - `while` → `WHILE`
  - `do` → `DO`
  - `break` → `BREAK`
  - `continue` → `CONTINUE`
  - `goto` → `GOTO`
- Data types:
  - `int` → `INT`
  - `char` → `CHAR`
  - `void` → `VOID`
- Functions/library:
  - `printf` → `PRINTF`
  - `scanf` → `SCANF`
- Other:
  - `typedef` → `TYPEDEF`
  - `return` → `RETURN`
  - `sizeof` → `SIZEOF`

Notes
- These are keyword token names returned by the lexer when an identifier lexeme matches a key in `reserved`.


---

# 10. Operators and Delimiters

The lexer defines tokens for operators and delimiters via module-level regex variables in `src/lexer.py`. Below each logical group is described along with the corresponding token names (as they appear in `utils/token.py` token list).

Arithmetic Operators
- Supported lexemes and token names:
  - `+`  → token: `PLUS` (t_PLUS = r'\\+')
  - `-`  → token: `MINUS` (t_MINUS = r'-')
  - `*`  → token: `MULTIPLY` (t_MULTIPLY = r'\\*')
  - `/`  → token: `DIVIDE` (t_DIVIDE = r'/')
  - `%`  → token: `MODULO` (t_MODULO = r'%')

Compound Assignment Operators
- Supported lexemes and token names:
  - `+=` → token: `PLUS_ASSIGN` (t_PLUS_ASSIGN = r'\\+=')
  - `-=` → token: `MINUS_ASSIGN` (t_MINUS_ASSIGN = r'-=')
  - `*=` → token: `MUL_ASSIGN` (t_MUL_ASSIGN = r'\\*=')
  - `/=` → token: `DIV_ASSIGN` (t_DIV_ASSIGN = r'/=')
  - `%=` → token: `MOD_ASSIGN` (t_MOD_ASSIGN = r'%=')

Increment and Decrement
- Supported lexemes and token names:
  - `++` → token: `INCREMENT` (t_INCREMENT = r'\\+\\+')
  - `--` → token: `DECREMENT` (t_DECREMENT = r'--')

Relational Operators
- Supported lexemes and token names:
  - `==` → token: `EQ` (t_EQ = r'==')
  - `!=` → token: `NE` (t_NE = r'!=' )
  - `<`  → token: `LT` (t_LT = r'<')
  - `>`  → token: `GT` (t_GT = r'>')
  - `<=` → token: `LE` (t_LE = r'<=')
  - `>=` → token: `GE` (t_GE = r'>=')

Logical Operators
- Supported lexemes and token names:
  - `&&` → token: `AND` (t_AND = r'&&')
  - `||` → token: `OR`  (t_OR = r'\|\|')

Unary Operators
- Supported lexemes and token names:
  - `!` → token: `NOT` (t_NOT = r'!')
  - `&` → token: `ADDRESS` (t_ADDRESS = r'&') — used to represent the C address-of operator

Assignment Operator
- `=` → token: `ASSIGN` (t_ASSIGN = r'=' )

Delimiters and Symbols
- Parentheses: `(` → `LPAREN`, `)` → `RPAREN`
- Braces: `{` → `LBRACE`, `}` → `RBRACE`
- Brackets: `[` → `LBRACKET`, `]` → `RBRACKET`
- Comma: `,` → `COMMA`
- Semicolon: `;` → `SEMI`
- Colon: `:` → `COLON`

Token precedence in PLY
- Because PLY resolves rules typically by regex match length and function order, longer sequences (`==`, `<=`, `++`, `+=`, etc.) are defined before their single-character counterparts to avoid incorrect splitting (e.g., `==` becomes `=` `=` if `=` is matched first).

---

# 11. Error Handling

Lexical errors occur when the input cannot be converted into valid tokens, such as illegal characters, unterminated literals, or malformed numeric constants.

## Error Detection

The lexer detects errors using:

- **Exclusive state handlers**:
  - `t_COMMENT_eof`, `t_STRING_eof`, and `t_CHAR_eof` handle unterminated comments, strings, and characters.
  - `t_STRING_newline` and `t_CHAR_newline` detect literals that incorrectly cross a newline.

- **Special validation rules**:
  - `t_INVALID_OCTAL` detects malformed octal literals such as `09` and `078`.
  - `t_error` handles unsupported characters like `@`, `$`, and `#`.

## Error Storage and Reporting

Errors are stored using:

- `lex_errors` — list containing detected lexical errors.
- `add_lex_error()` — appends new errors.
- `clear_errors()` — resets errors before a new lexer run.

After tokenization, `main.py` checks this list:
- If errors exist, they are displayed under `--- Lexical Errors Detected ---`.
- Otherwise, the generated token table is printed.

## Examples of Handled Errors

| Error Type | Example | Handling |
|---|---|---|
| Illegal character | `@`, `$`, `#` | Detected by `t_error` and skipped |
| Unterminated string | `"Hello` | Detected by STRING state EOF/newline handling |
| Unterminated character | `'A` | Detected by CHAR state EOF/newline handling |
| Unterminated comment | `/* comment` | Detected by COMMENT state EOF handling |
| Invalid octal | `09`, `078` | Detected by `t_INVALID_OCTAL` |
| Empty character | `''` | Detected during CHAR state closing |

## Error Recovery

The lexer records errors and continues scanning instead of terminating immediately. Invalid characters are skipped, and lexer states are restored when possible, allowing multiple errors to be reported in a single run.

Line numbers are maintained throughout normal lexing and inside exclusive states to provide accurate error locations.

---


# 12. Testing and Validation

Test methodology (as implied by repository)
- The repository includes a `test/` directory (used by `make test` and `run.sh`) with `.c` test files. Each test case is intended to validate specific lexer capabilities.
- `make test` prints tokenization results to stdout while iterating tests.
- `run.sh` runs the same loop and collects output into `output.txt` (creating a reproducible test report).

Types of tests you should expect / include
- Basic operators and delimiters: ensure `+`, `-`, `*`, `/`, `%`, parentheses, braces, semicolons, etc., tokenize correctly.
- Numeric literals: decimal, hexadecimal, binary, octal; invalid octal cases to confirm `t_INVALID_OCTAL`.
- Strings & Characters: valid strings & character constants, unterminated strings & chars, escaped characters.
- Comments: single-line `//` and multi-line `/* ... */` (including multi-line comment with nested newlines and unterminated comment).
- Identifiers and keywords: verification of reserved lookup and the `typedef` lexer hack (if typedefs are populated in tests).
- Error cases: illegal characters, unterminated constructs, empty character constants.
- Complex inputs: small functions, arrays, loops to validate that tokens are produced in correct order.


Validation approach
- Each test is expected to either produce the lexeme/token table (when no lexical errors) or to list lexical errors encountered while scanning the test input.
- `output.txt` created by `run.sh` is a persistent record for grading or debugging.


---

# 13. Conclusion

Phase 1 successfully implements a C-subset lexical analyzer using PLY in Python.

The lexer identifies keywords, identifiers, literals, operators, delimiters, and comments while also providing meaningful error reporting for invalid inputs such as illegal characters and unterminated constructs.

The generated token stream acts as the input for the parser in Phase 2. By separating token recognition from later checks like type validation and semantic rules, the lexer remains focused on converting source code into structured tokens.

Accurate tokenization and error handling simplify later compiler phases and make debugging easier by detecting and reporting issues early.

---
