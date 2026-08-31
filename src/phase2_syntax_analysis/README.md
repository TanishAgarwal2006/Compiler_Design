# Phase 2: Syntax Analysis

`parser.py` defines the PLY LALR grammar for the project’s C subset. A
successful parse returns the dataclass-based AST defined in `ast_nodes.py`.
Syntax and lexical errors are collected and reported with line information.

The grammar handles declarations, typedef names, array declarators and
initialisers, functions with parameters and calls, expressions with precedence,
all required loop forms, conditionals, labels, and jump statements. It parses
the language; it does not yet perform type checking, declaration checking, or
function argument validation.

After parsing, `common/symbol_classifier.py` walks the AST to label identifiers
as functions, variables, arrays, parameters, typedefs, or labels. This is a
reporting aid, not a complete semantic symbol table.

## Parsing method

PLY builds an LALR parser from the production functions in `parser.py`. Each
reduction creates an AST node instead of immediately evaluating code. Operator
precedence is declared from assignment through logical, relational, additive,
multiplicative, unary, and postfix expressions. A separate precedence level
for `IFX` resolves the usual dangling-`else` ambiguity by attaching `else` to
the nearest unmatched `if`.

## Design decisions and C-specific implementation choices

| Implementation choice | Standard C behaviour | Choice in this project and reason |
| --- | --- | --- |
| AST instead of direct evaluation | A compiler normally represents the parsed program internally before later stages analyse or translate it. | Every production creates dataclass AST nodes. TAC generation can therefore traverse a stable program representation rather than reparsing source text. |
| Function calls are syntax-only | Real C checks whether a called function exists and whether argument types/count match its declaration. | The parser accepts a callable expression with zero or more arguments. Existence, type compatibility, and return type are deferred to semantic analysis. This also permits recursive-call syntax. |
| `break`, `continue`, and `goto` are syntax-only | C requires `break`/`continue` inside suitable loops and requires every `goto` target to exist in the same function. | These constructs are parsed and stored in the AST. Loop context and label-target validation are not implemented yet; Phase 3 will also need this information to emit jumps. |
| Array dimensions are expressions | C supports constant expressions and, in some versions, variable-length arrays with detailed constraints. | One or more bracketed expressions are preserved as `ArrayDimension` AST nodes. The parser does not calculate sizes, verify dimensions, or lay out array memory. |
| Array initialisers are structural | C has detailed array-initialiser, aggregate, and string-literal rules. | Nested brace lists are represented as `InitializerList` nodes. Compatibility between declared type, dimension, and initializer is a later semantic check. |
| `printf`/`scanf` need no headers | Real C normally obtains their declarations from `<stdio.h>`. | Their dedicated lexical tokens are converted back to callable identifier nodes in the AST. This allows required I/O syntax without preprocessing or system headers. |
| No preprocessor | Standard C source may use `#include`, macros, and conditional compilation before parsing. | The input is parsed directly. Preprocessor directives are outside the language subset, so standard-header-based programs are not supported. |
| Parse success is not program correctness | A C compiler performs many semantic checks after parsing. | Success means the token sequence matches this grammar. It does not guarantee declared identifiers, valid types, valid return statements, or legal control-flow placement. |

## Use

```bash
python3 src/phase2_syntax_analysis/run_parser.py path/to/program.c
python3 src/phase2_syntax_analysis/run_parser.py path/to/program.c \
  --ast-file ast.txt --symbol-file symbols.txt
make parse FILE=path/to/program.c
make parse-phase2
make parse-all
```

The runner prints a parse result and symbol table, writes requested output
files, and stores a per-case report in `logs/`.

PLY may generate `parsetab.py` and `parser.out` while constructing the parser.
They are caches, not source files, and are ignored by Git.
