# Phase 1: Lexical Analysis

`lexer.py` uses PLY to scan the supported C subset and produce `(lexeme,
token_type)` pairs. It reports lexical errors with line numbers instead of
passing invalid input to the parser.

## Supported tokens

- Keywords: `int`, `char`, `void`, `typedef`, control-flow keywords,
  `return`, `printf`, `scanf`, and `sizeof`.
- Identifiers and typedef names.
- Decimal, hexadecimal, octal, and binary integer constants.
- Character and string literals, including supported single-character escapes.
- Arithmetic, assignment, relational, logical, increment/decrement, address,
  and delimiter tokens needed by Phase 2.

Line comments and block comments are skipped. Unterminated comments, strings,
and character constants are errors. Each analysis creates a fresh lexer so
state from one source file cannot affect the next one.

## Design decisions and C-specific implementation choices

| Implementation choice | Standard C behaviour | Choice in this project and reason |
| --- | --- | --- |
| `printf` and `scanf` are reserved tokens | They are library functions in C, so a normal compiler lexes them as identifiers and resolves declarations through headers and semantic analysis. | They are reserved as `PRINTF` and `SCANF` because they are required course features. The parser accepts them as callable names without implementing headers or a full library symbol table. |
| `sizeof` is reserved | `sizeof` is a C operator with special grammar: it can take an expression or a parenthesised type. | It has its own token and parser rules for `sizeof expr` and `sizeof(type)`. Its value is not calculated yet because storage layout belongs to later phases. |
| Typedef names can become `TYPENAME` tokens | C’s grammar is context-sensitive around typedef names. Real C implementations communicate typedef information between the parser and lexer. | Once the parser accepts `typedef int Count;`, it records `Count` on that lexer instance. Later occurrences are emitted as `TYPENAME`, which allows aliases to be used as types without a full C front end. |
| Multi-character character constants are rejected | C permits values such as `'AB'`; their numeric value is implementation-defined. | The project accepts exactly one ordinary character or one supported escape sequence. Rejecting multi-character constants gives predictable `char` behaviour for the future TAC/MIPS stages. |
| Integer bases include binary | Standard C supports decimal, octal (`012`), and hexadecimal (`0x12`). Binary (`0b1010`) was introduced only in newer C standards and is not universally supported by older compilers. | Decimal, octal, hexadecimal, and binary integers are recognised because they are useful test cases. Invalid octal values such as `09` are lexical errors. |
| `123abc` is split into two tokens | C requires token boundaries; this sequence is not a valid single integer or identifier token. | The lexer returns `INTEGER_CONSTANT(123)` then `IDENTIFIER(abc)`. The parser rejects the sequence when it cannot form a valid expression or declaration. This keeps token rules simple and leaves grammar validation to Phase 2. |
| Pointers are not supported | C uses `*` both for multiplication and pointer declarators, and `&` has pointer semantics. | `*` is only multiplication in declarations/expressions. `&` is accepted as a unary expression mainly for `scanf`, but pointer declarations and pointer type checking are not implemented. |
| Lexer state is isolated per file | Lexers retain internal state while processing comments and quoted literals. | `build_lexer()` creates a fresh lexer for each source input. An unterminated comment or string in one test cannot cause the next test file to be scanned in the wrong state. |

## Use

```bash
python3 src/phase1_lexical_analysis/run_lexer.py path/to/program.c
python3 src/phase1_lexical_analysis/run_lexer.py path/to/program.c --output tokens.txt
make lex FILE=path/to/program.c
make lex-phase1
make lex-all
```

The batch commands print a summary and write per-case reports under `logs/`.
