# Phase 1: Lexical analysis (cutting the text into tokens)

**Job:** read the C file and cut it into small pieces called *tokens*: a keyword like `while`, a name like `count`,
a number like `42`, a symbol like `+`. Every token gets a type name, for example `42` is `INTEGER_CONSTANT`.
Text that cannot be a token is a *lexical error*; it is reported with its line number and the later phases never see the file.

| File | What it does |
| --- | --- |
| `token_defs.py` | the keyword table (`while` -> `WHILE`) and the list of all token type names |
| `lexer.py` | the token rules, written with the PLY library (`ply.lex`) |

**Run it alone:** `bin/tacgen prog.c --tokens` prints the token table. The parser is not started, so this works even when the grammar is wrong.

## What the lexer accepts
- **Keywords:** types (`int char float double void bool short long signed unsigned auto`), `true false`, qualifiers and storage (`const volatile static extern typedef enum`),
  statements (`if else for while do until switch case default goto break continue return`), `sizeof`, `printf`, `scanf`.
  Words of features the compiler does not support (`struct union class public private protected this new delete`) are still recognised,
  so Phase 3 can say `unsupported feature` instead of a confusing syntax error.
- **Names:** letters, digits and `_`, not starting with a digit. A name introduced by `typedef` (or by `class X`) is a type name (`TYPENAME`) from then on.
  A class name directly followed by `(` becomes `CTOR_NAME` (a constructor or destructor name such as `Dog(` or `~Dog(`).
- **Numbers:** decimal `42`, hex `0x2A`, octal `052`, binary `0b101`, floats `3.14 .5 5. 1e3 2.5e-1 1.5f`. Integer suffixes `u l ul lu ll ull` (any case) are accepted and dropped.
- **Characters and strings:** `'a'`, `"hi\n"`. Escapes: `\n \t \r \a \b \f \v \? \\ \' \"`, octal `\101`, hex `\x41`.
- **Operators and punctuation:** all the C ones the project uses, including `::`, `->`, `...`.
- **Skipped:** `// ...` and `/* ... */` comments and preprocessor lines (`#include`, `#define`, `#ifdef` ...). There is no macro expansion: `#define` is read and ignored.

## Lexical errors (each is reported with its line)
illegal character (`@ $` and the like) · unterminated string · unterminated character · empty character `''` · more than one character `'AB'` ·
invalid escape (`'\q'`, `"\xz"`, `"\89"`) · non-ASCII character in a character constant · bad octal (`089`) · bad binary or hex (`0b12`, `0x`, `0xFG`) ·
malformed float (`1.2.3`, `1e`) · letters glued to a number (`12abc`, `45UU`) · unknown `#` directive · stray `#` · unterminated `/* ...` comment.

## Choices that differ from standard C
| Choice | Reason |
| --- | --- |
| `printf`, `scanf` are keywords | they are required features and no header files are read |
| one character (or one escape) between single quotes | gives a clear, predictable `char` value |
| `0b101` binary numbers accepted | handy in tests; recent C compilers accept them |
| `&` is one token for "address of" and "bitwise and" | the parser decides from the position, like C |
| class names followed by `(` are `CTOR_NAME` | lets the grammar tell a constructor from a type name |
| a new lexer is built for every file | an error in one file cannot affect the next |
