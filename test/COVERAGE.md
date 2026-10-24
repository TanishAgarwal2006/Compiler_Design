# Test coverage map

Which test file covers which feature. Paths are relative to `test/`. `P1V` = `phase1_lexical/valid`, `P1I` = `phase1_lexical/invalid`,
`P2V` = `phase2_syntax/valid`, `P2I` = `phase2_syntax/invalid`, `P3V` = `phase3_tac/valid`, `P3I` = `phase3_tac/invalid`, `U` = `unit`.
Where a feature appears in many files only the dedicated ones are named; the audit (last section) proves every item is hit at least once.

## Phase 1: lexical analysis

### Token types and keywords
| Feature | Covered by |
| --- | --- |
| `IDENTIFIER`, `INTEGER_CONSTANT`, `STRING_LITERAL`, `SEMI`, `COMMA`, `LPAREN/RPAREN`, `LBRACE/RBRACE`, `ASSIGN`, `PLUS`, `MULTIPLY`, `LT`, `GT`, `COLON` | every valid file; first stop `P1V/operators_punctuation.c` |
| `FLOAT_CONSTANT` | `P1V/numeric_literals.c`, `P1V/keywords_types_qualifiers.c` |
| `CHAR_CONSTANT` | `P1V/string_and_char_literals.c` |
| `TYPENAME` (typedef name becomes a type) | `P1V/keywords_types_qualifiers.c`, `P2V/declarations_types.c`, `P3V/declarations/typedef_adjacent.c` (name used right after its declaration) |
| `CTOR_NAME` (class name followed by `(`) | `P2V/classes_methods.c` |
| `SCOPE` `::`, `DOT`, `ARROW`, `ELLIPSIS`, `QUESTION`, `LBRACKET/RBRACKET` | `P1V/operators_punctuation.c`, `P2V/classes_methods.c`, `P2V/expressions_operators.c` |
| arithmetic `MINUS DIVIDE MODULO`, `INCREMENT DECREMENT` | `P1V/operators_punctuation.c`, `P2V/expressions_operators.c` |
| assignments `PLUS_ASSIGN MINUS_ASSIGN MUL_ASSIGN DIV_ASSIGN MOD_ASSIGN AND_ASSIGN OR_ASSIGN XOR_ASSIGN LSHIFT_ASSIGN RSHIFT_ASSIGN` | `P1V/operators_punctuation.c`, `P2V/expressions_operators.c` (`AND_ASSIGN OR_ASSIGN XOR_ASSIGN` only there) |
| bit operators `ADDRESS` (`&`), `BIT_OR`, `BIT_XOR`, `BIT_NOT`, `LSHIFT`, `RSHIFT` | `P1V/operators_punctuation.c`, `P2V/expressions_operators.c` |
| comparison and logic `EQ NE LT LE GT GE AND OR NOT` | `P1V/operators_punctuation.c`, `P2V/expressions_operators.c` |
| control keywords `if else for while do goto break continue switch case default return until` | `P1V/keywords_control_flow.c`, `P2V/control_flow.c`, `P3V/control_flow/control_flow.c`, `P3V/control_flow/until.c` |
| type keywords `int char void float double bool _Bool short long signed unsigned true false` | `P1V/keywords_types_qualifiers.c` (`bool` also `P2V/declarations_types.c`) |
| qualifiers and storage `const volatile static extern typedef auto` | `P1V/keywords_types_qualifiers.c`, `P2V/declarations_types.c` (`extern`, `static`) |
| aggregates `struct union enum` | `P1V/keywords_types_qualifiers.c`, `P2V/structs_unions_enums.c` |
| class words `class public private protected this new delete` | `P1V/keywords_classes_lambdas.c`, `P2V/classes_methods.c` |
| built-ins `printf scanf sizeof` | `P1V/keywords_functions_memory_file_io.c`, `P1V/keywords_types_qualifiers.c`, `P3V/input_output/input_output.c` |
| file-I/O and memory names (`fopen`, `malloc`, ... are plain identifiers) | `P1V/keywords_functions_memory_file_io.c`, `P2V/io_memory_file.c` |

### Literals
| Feature | Covered by |
| --- | --- |
| decimal, hex (`0x 0X`, mixed case), octal (`017`, `00`), binary (`0b 0B`) | `P1V/numeric_literals.c`; values: `U/test_literals.py` |
| integer suffixes `u l ul lu ll ull` (any case) | `P1V/numeric_literals.c` |
| floats: `3.14 .5 5. 1e3 2.5e-1 1E+2 1.5f 3e2f` | `P1V/numeric_literals.c`, `P3V/types/types.c` |
| char literals, all escapes `\n \t \r \b \f \v \a \0 \\ \' \? \101 \x41` | `P1V/string_and_char_literals.c`, `U/test_literals.py` (`test_char_value_*`) |
| string literals, all escapes, quotes/comment markers inside, adjacent literals, `char s[] = "..."` | `P1V/string_and_char_literals.c`, `U/test_literals.py` (`test_string_bytes_*`), `P3V/strings/strings.c` |
| literals carry line numbers into the tree | `U/test_literals.py::test_ast_nodes_carry_line_numbers` |

### Comments and preprocessor
| Feature | Covered by |
| --- | --- |
| `//` and `/* */` comments (inline, multi-line, nested markers, `/**/`) | `P1V/comments_and_preprocessor.c` |
| `#include #define #undef #ifdef #ifndef #if #elif #else #endif #pragma #line #warning #error`, indented `#` | `P1V/comments_and_preprocessor.c` |

### Lexical errors
| Error message | Covered by |
| --- | --- |
| Illegal character (`@ $` backquote backslash) | `P1I/symbols_buggy.c` |
| Unterminated string literal | `P1I/strings_chars_buggy.c` (line 7), `P1I/string_eof_buggy.c` (at end of file) |
| Invalid escape sequence in string (`\xz`, `\89`, `\q`) | `P1I/strings_chars_buggy.c` |
| Empty character constant `''` | `P1I/strings_chars_buggy.c` |
| Invalid escape sequence in character constant | `P1I/strings_chars_buggy.c` |
| Multi-character constant (`'AB'`, `'\n\n'`) | `P1I/strings_chars_buggy.c` |
| Non-ASCII character in character constant | `P1I/strings_chars_buggy.c` |
| Unterminated character constant | `P1I/strings_chars_buggy.c` (line 6), `P1I/char_eof_buggy.c` (at end of file) |
| Unknown preprocessor directive, stray `#` | `P1I/preprocessor_comments_buggy.c` |
| Unterminated block comment | `P1I/preprocessor_comments_buggy.c` |
| Invalid octal literal `089` | `P1I/numbers_buggy.c` |
| Invalid binary / hex literal (`0b1102`, `0x`, `0b`, `0xFG`) | `P1I/numbers_buggy.c` |
| Malformed float (`1.2.3`, `1e`) | `P1I/numbers_buggy.c` |
| Letters glued to a number (`12abc`, `45UU`) | `P1I/numbers_buggy.c` |
| `--tokens` stops before the parser | `U/test_cli.py::test_tokens_only_stops_before_the_parser` |

## Phase 2: syntax analysis

### Grammar constructs (all in `P2V`; `P3V` adds the ones the compiler can run)
| Construct | Covered by |
| --- | --- |
| variable declarations, initialisers, multiple declarators, `const volatile static extern` | `P2V/declarations_types.c` |
| `typedef` (also of arrays, function pointers, structs) | `P2V/declarations_types.c`, `P2V/structs_unions_enums.c`, `P3V/declarations/typedef_adjacent.c` |
| `enum` / `Enumerator` | `P2V/structs_unions_enums.c`, `P3V/declarations/declarations.c` |
| `struct`, `union` | `P2V/structs_unions_enums.c` |
| `class`, access labels, base classes, constructors, destructors, `Class::method` outside the class, `this` | `P2V/classes_methods.c` |
| arrays, multi-dimensional, initialiser lists (`InitializerList` is built only by `P3V` and `U` programs), pointers, `&`, `*` | `P2V/arrays_pointers.c`, `P3V/arrays/arrays.c` |
| functions: parameters, prototypes, `void` parameter, variadic `...`, function pointers | `P2V/functions.c`, `P2V/expressions_operators.c` (`VarArgsParameter`) |
| every expression operator and priority, `?:`, comma, casts, `sizeof`, compound assignments, `++ --` | `P2V/expressions_operators.c`, `P3V/arithmetic/arithmetic.c` |
| `if/else` (dangling else), `while`, `do-while`, `until`, `do-until`, `for` (with/without declaration) | `P2V/control_flow.c`, `P3V/control_flow/control_flow.c`, `P3V/control_flow/until.c` |
| `switch/case/default`, labels, `goto`, `break`, `continue`, `return` | `P2V/control_flow.c`, `P3V/control_flow/control_flow.c` |
| `new`, `delete`, `delete[]`, file I/O and memory calls | `P2V/io_memory_file.c` |
| lambdas, `auto`, references | `P2V/lambdas_auto_references.c` |
| member access `.` `->`, qualified names | `P2V/structs_unions_enums.c`, `P2V/classes_methods.c`, `P2V/io_memory_file.c` |
| AST printing (`--ast`) | `U/test_cli.py::test_ast_dump` |

### Syntax errors and recovery (each `[n]` block of an `_buggy.c` file is one case; `[accepted]`, `[boundary]` and `[stricter]` blocks pin what is NOT an error)
| Area | Covered by |
| --- | --- |
| missing `;`, `)`, `]`, extra `)`, empty `()`, dangling operator, trailing/double comma, `delete[` | `P2I/statements_expressions_buggy.c` |
| `if`, `while`, `until`, `for`, `switch`, `case` headers; stray `case`/`default`; `break`/`continue` outside a loop accepted | `P2I/control_flow_buggy.c` |
| missing `;`, missing initialiser, unknown type name, bad `{ }` list, bare expression at file scope, bare `int;`/`typedef int;` | `P2I/declarations_buggy.c` |
| array declarator / subscript, `&` and `*` with no operand, function-pointer declarator, bad cast, empty `sizeof()` | `P2I/arrays_pointers_buggy.c` |
| missing return type, bad parameter list, `...` alone, missing `)` and missing `}` of a function body | `P2I/functions_buggy.c` |
| struct / union / enum / class mistakes, bad inheritance list, bad constructor and destructor | `P2I/aggregates_buggy.c` |
| `goto` and label mistakes, misspelt class in `Class::method`, `::` in expressions | `P2I/forward_refs_scope_buggy.c` |
| lambda capture list, `?:` without `:`, `printf`/`scanf`/`malloc`/`fprintf` argument lists, `sizeof` parens, bad `new` | `P2I/lambdas_builtins_buggy.c` |
| `fopen fclose fread fwrite fprintf fscanf fgets fputs feof` call mistakes | `P2I/file_io_buggy.c` |
| recovery: one mistake reported once, later mistakes still found, second message for the closing `}` | `P2I/cascading_recovery_buggy.c`, `P2I/do_while_recovery_buggy.c`, `U/test_syntax_messages.py::test_parser_recovers_and_reports_each_bad_statement_once` |
| message `unexpected token 'x' ... missing ';' at the end of line N` hint, and the plain message without a hint | `U/test_syntax_messages.py` (`test_missing_semicolon_hint_points_at_the_previous_line`, `test_plain_unexpected_token_has_no_hint`) |
| message `unexpected end of file, a '}' or ';' is probably missing` | `P2I/functions_buggy.c` [6], `U/test_syntax_messages.py::test_end_of_file_message` |
| lexical errors stop the compiler before Phase 2 | `U/test_cli.py::test_errors_exit_1_and_write_nothing` |

## Phase 3: semantic analysis, IR, interpreter

### Semantic errors (each message has a line in the `.err` file of the named case)
| Error | Covered by |
| --- | --- |
| undeclared identifier / unknown function / `X is not a function` | `P3I/declarations/declarations_buggy.c`, `P3I/functions/functions_buggy.c` |
| redeclaration, redefinition of function, conflicting prototype types, different kind of symbol | `P3I/declarations/declarations_buggy.c`, `P3I/declarations/declarations_more_buggy.c` |
| reserved name (`atoi`, `printf`, `scanf`) redefined | `P3I/declarations/declarations_buggy.c` |
| `extern` never defined, variable of type `void`, unknown enum, braces around scalar initialiser | `P3I/declarations/declarations_buggy.c`, `declarations_more_buggy.c` |
| parameter: `void`, unnamed in a definition, duplicate; function returning an array | `P3I/declarations/declarations_more_buggy.c` |
| missing `main`, bad `main` signature | `P3I/declarations/missing_main_buggy.c`, `P3I/declarations/bad_main_signature_buggy.c` |
| wrong argument count / type, return type, missing or extra return value | `P3I/functions/functions_buggy.c` |
| `break` / `continue` outside a loop, `goto` to missing label, duplicate label | `P3I/control_flow/control_flow_buggy.c` |
| duplicate `case`, duplicate `default`, non-constant / non-integer case value, non-int `switch` | `P3I/control_flow/control_flow_buggy.c`, `P3I/control_flow/switch_case_buggy.c`, `P3I/types/types_buggy.c` |
| array: missing size, non-positive or non-constant size, `void` element, too many subscripts, non-array subscript, non-int index | `P3I/arrays/arrays_buggy.c`, `P3I/arrays/arrays_init_buggy.c` |
| array initialisers: too many, too many braces, mixed nested/flat, string too long, string into int array, wrong element type, non-constant global | `P3I/arrays/arrays_init_buggy.c`, `P3I/arrays/arrays_buggy.c` |
| global initialiser not constant / must be a string literal | `P3I/declarations/declarations_buggy.c`, `P3I/arrays/arrays_init_buggy.c` |
| passing an array / element with the wrong shape | `P3I/arrays/arrays_buggy.c` |
| assignment to array, `const`, non-variable; wrong initialiser type | `P3I/types/types_buggy.c`, `P3I/types/types_ops_buggy.c` |
| operator operand types (`% & ~ - += %=`), `++` on wrong type, `?:` branch mismatch, bad cast, `sizeof(void)`, `void` value used, function used as a value | `P3I/types/types_buggy.c`, `P3I/types/types_ops_buggy.c` |
| division by constant zero (`/` and `/=`) | `P3I/types/types_buggy.c`, `P3I/types/types_ops_buggy.c` |
| non-numeric `if` condition | `P3I/types/types_buggy.c` |
| `printf`/`scanf`: missing or non-literal format, bad specifier, lone `%`, count mismatch, wrong type, `&` missing, `%s` without char array, extra text in scanf format | `P3I/input_output/input_output_buggy.c`, `P3I/input_output/printf_scanf_buggy.c` |
| `atoi` argument count / type | `P3I/input_output/printf_scanf_buggy.c` |
| using the value of `printf` | `P3I/input_output/unsupported_printf_value_buggy.c`, `U/test_tac_basic.py::test_printf_value_is_rejected` |
| one mistake gives one error; errors sorted by line; errors reach the shared list | `U/test_semantic.py` (`test_one_mistake_gives_one_error`, `test_errors_sorted_by_line_with_line_numbers`, `test_semantic_errors_reach_shared_list`) |

### Unsupported features (`unsupported feature: ...`)
| Feature | Covered by |
| --- | --- |
| pointers other than `char *`, pointer dereference, casts to pointer types | `P3I/unsupported/unsupported_buggy.c`, `unsupported_more_buggy.c` |
| `&` outside `scanf` | `P3I/unsupported/unsupported_buggy.c` |
| `struct`, `union` | `P3I/unsupported/unsupported_buggy.c`, `unsupported_more_buggy.c` |
| classes, constructors / destructors / `Class::method`, member calls, `this` | `P3I/unsupported/unsupported_buggy.c`, `unsupported_more_buggy.c`; `U/test_defensive.py::test_member_function_declarator` |
| `new`, `delete` | `P3I/unsupported/unsupported_buggy.c`, `unsupported_more_buggy.c` |
| lambdas, `auto`, references | `P3I/unsupported/unsupported_buggy.c`, `unsupported_more_buggy.c` |
| function pointers (only direct calls) | `P3I/unsupported/unsupported_buggy.c` |
| variadic functions, `static` locals | `P3I/unsupported/unsupported_buggy.c` |
| `malloc`/`free`, file I/O (`fopen`, `fclose`), `FILE` | `P3I/unsupported/unsupported_buggy.c` |
| passing a row of a 2-D array | `P3I/unsupported/pass_row_buggy.c` |
| defensive branches that valid parsing cannot reach (unknown node, literal or operator kind) | `U/test_defensive.py` |

### Valid programs (IR run in the interpreter and compared with gcc)
| Feature | Covered by |
| --- | --- |
| int / char / float / bool, conversions, `short long unsigned` as `int`, wrap-around, casts | `P3V/types/types.c`, `P3V/arithmetic/arithmetic.c`, `U/test_tac_basic.py::test_end_to_end_conversions` |
| all operators, constant folding | `P3V/arithmetic/arithmetic.c`, `U/test_semantic.py::test_constant_folding_c_semantics` |
| `if`, loops, `until`, `switch` fall-through, `goto`, short-circuit `&& ||` | `P3V/control_flow/control_flow.c`, `P3V/control_flow/until.c`, `U/test_control_flow.py` |
| arrays 1-3 dimensions, global arrays, initialisers, array parameters | `P3V/arrays/arrays.c`, `U/test_arrays.py` |
| strings, `char *`, `char s[]`, `%s`, `argv`, `atoi` | `P3V/strings/strings.c`, `P3V/strings/strings_argv.c`, `P3V/input_output/command_line.c` |
| functions, recursion, mutual recursion, prototypes, user `print_int` etc. (`.u` names) | `P3V/functions/functions.c`, `U/test_calls_io.py`, `U/test_tac_basic.py::test_variables_named_like_temps_and_ir_words_still_work` |
| `printf`, `scanf`, scanf return values and mismatch | `P3V/input_output/input_output.c` (+ `.in`), `P3V/input_output/scanf_empty_input.c` |
| globals, `typedef`, `enum`, `const`, `extern`, `static`, shadowing | `P3V/declarations/declarations.c`, `P3V/declarations/typedef_adjacent.c` |

### IR instructions
| Instruction | Covered by |
| --- | --- |
| copy `x = y`; integer binary ops; compare and jump `if .. goto`, `goto`, labels | every `P3V` case; `U/test_tac_basic.py` |
| float ops `+f -f *f /f <f <=f >f >=f ==f !=f` | `P3V/arithmetic`, `P3V/types`, `P3V/arrays`, `P3V/functions`; `U/test_tac_basic.py::test_spec_float_example` |
| unary `- ~ ! -f` | `P3V/arithmetic` (`- ~ !`), `P3V/types` (`-f`); `U/test_tac_basic.py::test_not_on_float_compares_with_zero` |
| `i2f`, `f2i`, `i2c` | `P3V/types/types.c`, `P3V/functions/functions.c`; `U/test_tac_basic.py::test_float_to_char_goes_through_int` |
| array load `x = a[off]` / store `a[off] = y` | `P3V/arrays/arrays.c`; `U/test_arrays.py` |
| `param`, `x = call f, n`, `call f, n`, `return`, `return y` | `P3V/functions/functions.c`; `U/test_calls_io.py::test_args_evaluated_before_params` |
| `.data` strings, `global` scalar and array, `local`, `temp`, `endfunc` | `P3V/declarations`, `P3V/arrays`; `U/test_tac_basic.py::test_file_layout` |
| built-ins `print_int print_char print_str print_float` | `P3V/input_output/input_output.c`, `P3V/types/types.c` |
| built-ins `read_int read_char read_float read_str scan_status` | `P3V/input_output/input_output.c`, `P3V/input_output/scanf_empty_input.c`; `U/test_calls_io.py` |
| built-in `atoi` | `P3V/strings/strings_argv.c`, `P3V/input_output/command_line.c` |

### IR interpreter errors (`U/test_ir_errors.py::test_every_ir_error_message` runs them all)
Load-time `IRError`: expected `.data`/`.text`, string ends with backslash, unknown escape, bad data line, bad func header, bad parameter,
function or global defined twice, bad temp declaration, name declared twice, undefined name / label / function, assign to array,
not an array or string, label defined twice, param without call, bad instruction, unknown comparison / operator, operand type mismatch,
must return / void returns a value, wrong parameter count or type, call has too few `param`s, returns no value, bad initial value,
array initialiser not in braces, no `main`, bad `main` signature.
Run-time `RunError`: division by zero (`/` and `%`), out of memory (stack overflow), address out of range, control reaches end without return,
step limit exceeded, call stack too deep. Also `U/test_tac_basic.py::test_interpreter_strictness`, `test_interpreter_step_limit`, `test_interpreter_deep_recursion`.

### Command-line options (`U/test_cli.py`, `U/test_tac_basic.py`)
| Option | Covered by |
| --- | --- |
| (none) `Syntax analysis: OK` | `test_default_run_reports_syntax_ok` |
| `--tokens` | `test_tokens_only_stops_before_the_parser` |
| `--ast` | `test_ast_dump` |
| `--symbols` | `test_symbols_report`, `test_all_name_roles_are_labelled` |
| `--semantic` | `test_semantic_table` |
| `--all` | `test_all_name_roles_are_labelled` |
| `--tac` (IR to the screen only) | `test_tac_printed_and_written`, `U/test_tac_basic.py::test_cli_tac_to_stdout_is_only_ir` |
| `-o FILE` | `test_tac_printed_and_written`, `U/test_tac_basic.py::test_cli_compile_and_run` |
| exit code 1 and no IR file on error | `test_errors_exit_1_and_write_nothing`, `U/test_tac_basic.py::test_cli_error_writes_no_ir_file` |
| missing source file | `test_missing_source_file` |

## The audit: `tools/coverage_audit.py`
Run `python3 tools/coverage_audit.py` from the project folder (needs PLY). It runs every `test/**/*.c` and every `test/unit/test_*.py` in-process and checks that each of these was hit at least once:
- every token type in `token_defs.tokens` and every keyword spelling in `token_defs.reserved`;
- every AST node class in `ast_nodes.py` (built by the parser at least once);
- every source line in `src/` that reports an error (`add_*_error`, `self.err`, `self.unsupported`, `GenError`, `IRError`, `RunError`).

It prints `ALL COVERED` per group and exits 0, or lists what is missing and exits 1. It does not check that the right message text is produced; the `.err` files and `U/` tests do that.
