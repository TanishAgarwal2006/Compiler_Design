# Phase 2: Syntax analysis (checking the grammar and building the program tree)

**Job:** take the tokens and check that they follow the grammar of the language. If they do, build a *tree* of the program (the AST):
for `a = b + 1;` the tree has an "assignment" node with `a` on one side and an "addition" node on the other. Later phases walk this tree
instead of reading text again. If the grammar is broken, report each mistake with its line number.

| File | What it does |
| --- | --- |
| `parser.py` | the grammar rules, written with PLY (`ply.yacc`). Each rule that matches builds one tree node |
| `ast_nodes.py` | one small class per kind of tree node, and `format_ast()` that prints the tree |
| `../common/symbol_classifier.py` | only labels names (function, variable, array...) for the printed reports; never used to check the program |

**Run it:** `bin/tacgen prog.c` (check only), `--ast` (print the tree), `--symbols` (labelled names).

## What the grammar covers
- Declarations: variables, multi-dimensional arrays, initialiser lists, `typedef`, `enum`, `struct`/`union`, `const`, `volatile`, `static`, `extern`.
- Functions: parameters, prototypes, calls, pointer- and reference-returning functions, function pointers, variadic `...`.
- Every expression operator with the correct priority, casts, `sizeof`, `?:`, comma, `new`, `delete`, `Class::name`, member access `.` and `->`.
- Statements: `if/else`, `for` (with or without a declaration), `while`, `do-while`, `until`, `do-until`, `switch/case/default`, labels, `goto`, `break`, `continue`, `return`.
- C++-style extras: classes with access labels and base classes, constructors, destructors, methods defined outside the class (`int Dog::bark() {}`),
  `this`, lambdas (`[a, &b](int x) -> int { ... }`), `auto`, references (`int &r`).

The compiler cannot *compile* many of these (pointers, classes, lambdas...). The parser accepts them anyway so that Phase 3 can answer
`unsupported feature: ...`, which is clearer than a syntax error.
Parsing only proves that the words are in a legal order. It does not check that names are declared or that types match; that is Phase 3.

## How it works
- PLY builds the parser from the rules in `parser.py` (an LALR(1) table). PLY writes `parsetab.py` and `parser.out` next to `parser.py` as caches; they are not part of the project.
- Operator priority is declared once: assignment is lowest, then `?:`, `||`, `&&`, `|`, `^`, `&`, equality, comparison, shifts, `+ -`, `* / %`, unary, postfix.
- `if (a) if (b) x; else y;`: the `else` belongs to the nearest `if` (settled by a priority rule, so PLY reports no conflict).
- A typedef name or class name is remembered by the lexer as soon as it is declared, so `Node *next;` inside `class Node { ... }` already sees `Node` as a type.

## Syntax errors
- Each error shows the line and the source text. A statement that lacks its `;` is reported at the line that needs it:
  `unexpected token 'return' (is a ';' missing at the end of line 3?)`.
- Recovery: after an error the parser skips to the next `;` or `}` and carries on, so one mistake is usually reported once and later mistakes are still found.
  The tree can then be incomplete, so the compiler never goes on to Phase 3 when Phase 1 or 2 found an error. One broken block can still cause a second message for its closing `}`.
- If the file ends too early (a missing `}`) the message says so.

## Choices
| Choice | Reason |
| --- | --- |
| build a tree, do not generate code while parsing | Phase 3 can check types first and generate code in a second walk |
| calls, `break`, `continue`, `goto` are only checked for grammar here | names, types and loop context need declarations: Phase 3 |
| array sizes are kept as expressions | Phase 3 works out the numbers |
| `printf`/`scanf` are ordinary call nodes | no header files needed |
| `case`/`default` are only allowed inside a `switch` | they are part of the switch rule |
