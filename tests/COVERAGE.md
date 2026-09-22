# Test Coverage Map

One row per feature/error category, pointing at the file that demonstrates
it. Consolidated from a previous suite of one-file-per-feature tests; see
the file header comments (`// Covers: ...`) for the exact list each file
carries.

## Phase 1 — Lexical (`tests/phase1_lexical/`)

### valid/

| Feature | File |
| --- | --- |
| Reserved keywords (`if`, `else`, `for`, `while`, `do`, `break`, `continue`, `goto`, `typedef`, `return`, `printf`, `scanf`, type names) | `valid/general_tokens.c` |
| Delimiters (`{} () [] ; , :`) | `valid/general_tokens.c` |
| Arithmetic operators (`+ - * / %`) | `valid/general_tokens.c` |
| Compound assignment (`+= -= *= /= %=`) | `valid/general_tokens.c` |
| Increment/decrement (`++ --`, prefix and postfix) | `valid/general_tokens.c` |
| Relational operators (`== != < <= > >=`) | `valid/general_tokens.c` |
| Logical operators (`&& \|\| !`) | `valid/general_tokens.c` |
| Decimal integer literals | `valid/numeric_literals.c` |
| Hexadecimal literals (`0x2A`) | `valid/numeric_literals.c` |
| Octal literals (`052`) | `valid/numeric_literals.c` |
| Binary literals (`0b101010`) | `valid/numeric_literals.c` |
| String literals | `valid/string_and_char_literals.c` |
| Char literals + escape sequences (`\n \t \'`) | `valid/string_and_char_literals.c` |
| Line comments (`//`) | `valid/comments_and_preprocessor.c` |
| Block comments (`/* */`, multi-line) | `valid/comments_and_preprocessor.c` |
| Preprocessor directives (`#include`, `#define`) | `valid/comments_and_preprocessor.c` |
| Float literals (plain, exponent, leading-dot, `f` suffix) | `valid/comments_and_preprocessor.c` |

### invalid/

| Error category | File |
| --- | --- |
| Illegal character (`@`) | `invalid/illegal_character.c` |
| Unterminated string literal | `invalid/unterminated_string.c` |
| Unterminated char literal | `invalid/unterminated_char.c` |
| Invalid octal literal (bad digit) | `invalid/invalid_octal_literal.c` |
| Multi-character constant (`'AB'`) | `invalid/multi_character_constant.c` |
| Empty character constant (`''`) | `invalid/empty_character_constant.c` |
| Unterminated block comment | `invalid/unterminated_block_comment.c` |
| Malformed float (two decimal points) | `invalid/malformed_float.c` |
| Unknown preprocessor directive (`#includ`) | `invalid/unknown_directive.c` |

These 9 stayed one-file-per-category rather than being merged: each is
already a single, minimal, distinct lexical error, and merging any of them
would put more than one deliberate error in one file — which is exactly
what the invalid-file design rule (one unambiguous cause of failure per
file) rules out.

## Phase 2 — Syntax (`tests/phase2_syntax/`)

### valid/

| Feature | File |
| --- | --- |
| Arithmetic/relational/logical operators | `valid/expressions_and_operators.c` |
| Unary operators (`- + --`) | `valid/expressions_and_operators.c` |
| Operator precedence & associativity (incl. right-assoc chained `=`) | `valid/expressions_and_operators.c` |
| Compound assignment precedence | `valid/expressions_and_operators.c` |
| `if`/`else if`/`else` | `valid/control_flow.c` |
| Dangling-else attachment | `valid/control_flow.c` |
| `for` (incl. `for (;;)` and a declaration in the init slot, `for (int i = 0; ...)`) | `valid/control_flow.c` |
| `while` (incl. empty body, `;`-only body) | `valid/control_flow.c` |
| `do`-`while` | `valid/control_flow.c` |
| `switch`/`case`/`default` (incl. fall-through case labels and an empty `switch (x) { }` body) | `valid/control_flow.c` |
| `break` / `continue` | `valid/control_flow.c` |
| `goto` and labels | `valid/control_flow.c` |
| Integer arrays | `valid/arrays_and_pointers.c` |
| Char arrays (incl. string-initialized array) | `valid/arrays_and_pointers.c` |
| Multidimensional arrays (2D and 3D) | `valid/arrays_and_pointers.c` |
| Complex indexing (expressions and function calls as indices) | `valid/arrays_and_pointers.c` |
| `argc`/`argv`-style parameters (`int argc, char *argv[]`) | `valid/arrays_and_pointers.c` |
| Pointers, address-of / dereference (`& *`) | `valid/arrays_and_pointers.c` |
| Multi-level pointers (`**pp`) | `valid/arrays_and_pointers.c` |
| `struct` definition and member access (`.`) | `valid/structs_unions_enums.c` |
| Pointer-to-struct member access (`->`) | `valid/structs_unions_enums.c` |
| `enum` (implicit values, explicit values) | `valid/structs_unions_enums.c` |
| `union` | `valid/structs_unions_enums.c` |
| `typedef` | `valid/structs_unions_enums.c` |
| Function calls with arguments | `valid/functions_and_recursion.c` |
| Recursive function calls | `valid/functions_and_recursion.c` |
| Function pointers (declaration, assignment, call through) | `valid/functions_and_recursion.c` |
| Empty `(void)` parameter list | `valid/functions_and_recursion.c` |
| Unnamed (abstract) parameters (`int f(int, int);`) | `valid/functions_and_recursion.c` |
| `printf`/`scanf` with multiple arguments | `valid/io_and_input.c` |
| Reading a variable-length series of values (command-line-style input) | `valid/io_and_input.c` |
| `float` / `double` | `valid/types_and_qualifiers.c` |
| Integer size/sign modifiers (`unsigned long`, `signed char`, `short`) | `valid/types_and_qualifiers.c` |
| `const` | `valid/types_and_qualifiers.c` |
| `static` / `extern` | `valid/types_and_qualifiers.c` |
| `bool` / `true` / `false` | `valid/types_and_qualifiers.c` |
| `class` definition and member functions | `valid/classes.c` |
| Inheritance (`class Dog : public Animal`) | `valid/classes.c` |
| `public` / `private` / `protected` access labels | `valid/classes.c` |
| Multiple declarators sharing one type (`int a, b = 5, arr[10];`) | `valid/declarations_and_blocks.c` |
| Empty statements (`;`) | `valid/declarations_and_blocks.c` |
| Nested compound blocks | `valid/declarations_and_blocks.c` |
| Bitwise operators (`\| ^ ~ << >>`) and compound-assignment forms | `valid/bitwise_ternary_and_variadic.c` |
| Ternary operator (`?:`), including nesting | `valid/bitwise_ternary_and_variadic.c` |
| `until` / `do`-`until` loops | `valid/bitwise_ternary_and_variadic.c` |
| Variadic parameters (`...`) | `valid/bitwise_ternary_and_variadic.c` |
| `new` (plain, array form `new T[n]`, constructor-args form `new T(args)`) | `valid/new_delete_and_scope.c` |
| `delete` / `delete[]` | `valid/new_delete_and_scope.c` |
| Scope resolution (`::`) for a base-class/static member | `valid/new_delete_and_scope.c` |

### invalid/

| Error category | File |
| --- | --- |
| Missing semicolon | `invalid/missing_semicolon.c` |
| Unbalanced parentheses | `invalid/unbalanced_parentheses.c` |
| Missing closing brace | `invalid/missing_brace.c` |
| `if` condition missing parentheses | `invalid/missing_condition_parens.c` |
| Function call missing argument separator | `invalid/bad_function_call_syntax.c` |
| `case` label missing its colon | `invalid/bad_switch_case.c` |
| `delete[` missing its closing bracket | `invalid/bad_delete_syntax.c` |

Error reporting uses panic-mode recovery (`error SEMI` at both statement and
top-level scope, per the standard yacc/PLY pattern - see `p_statement_error`
/ `p_external_declaration_error` in `parser.py`): after a syntax error, the
parser discards tokens up to the next `;` and resumes there, rather than
re-reporting an error for every token until EOF. Each file above now
reports one error per genuine problem instead of a cascade.

## Known gaps (deliberately out of scope for this round)

- **Reference declarators** (`int &r = x;`) - not implemented. The AST's
  `Declarator` node carries an `is_reference` field for this, but no
  grammar rule sets it yet.
- **File manipulation** (`fopen`/`fread`/etc.) - not implemented; no
  tokens or grammar rules exist for it.
- **Lambda functions** - not implemented.

Everything else accepted by the grammar (see
`src/phase1_lexical_analysis/token_defs.py` and
`src/phase2_syntax_analysis/parser.py`) has at least one test exercising
it, and every previously-unused lexer token (`NEW`, `DELETE`, `SCOPE`) is
wired into a grammar rule and covered by a test - PLY's grammar build
reports no unused-token warnings, and no unexpected grammar conflicts
(the shift/reduce count is exactly 1, the pre-existing cast-rule
ambiguity).
