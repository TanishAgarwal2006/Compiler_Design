# Phase 3: Three-Address Code

This phase is not implemented. The directory exists to keep the compiler
pipeline organised.

The next implementation should translate the Phase 2 AST to TAC quadruples:

```text
(op, arg1, arg2, result)
```

It will need temporary and label generation, scoped symbols, expression and
assignment lowering, control-flow jumps, array index/address calculations,
and `param`/`call`/`return` instructions for function calls and recursion.

Recommended modules are `tac.py`, `ir_generator.py`, and `symbol_table.py`.
Add expected-TAC tests under `tests/phase3_intermediate_code/` when the phase
is started.

## Intended design decisions

| Design choice | Why it fits this compiler |
| --- | --- |
| Quadruples `(op, arg1, arg2, result)` | They are simple to print, test, optimise, and lower to MIPS. They also make temporary values explicit. |
| Explicit labels and jumps | `if`, loops, `break`, `continue`, and `goto` all reduce naturally to labels, conditional jumps, and unconditional jumps. |
| Per-function symbol scopes | TAC needs storage/type information for local variables, parameters, globals, and arrays. A scoped table is more useful than the current reporting-only classifier. |
| Row-major array offsets | C arrays are row-major. A multidimensional access such as `a[i][j]` must be translated to a linear offset before MIPS code can load or store it. |
| `param`, `call`, and `return` instructions | These make argument passing and results visible in the IR and provide a clear foundation for recursive MIPS calls. |
