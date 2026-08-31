# Phase 4: Optimisation and MIPS Generation

This phase is not implemented. It will consume TAC from Phase 3 and emit MIPS
assembly.

The initial implementation should favour correctness over aggressive
optimisation: create basic blocks, fold constants, remove simple dead code,
assign temporary registers with stack spills, create a stack frame per
function, and lower calls, arrays, and supported `printf`/`scanf` operations.
Correct stack-frame handling is required for recursive calls.

Suggested modules are `optimizer.py`, `mips_generator.py`, and
`register_allocator.py`. Add expected assembly tests under
`tests/phase4_optimization_codegen/`; ideally run them with SPIM, MARS, or an
equivalent MIPS simulator.

## Intended design decisions

| Design choice | Why it fits this compiler |
| --- | --- |
| Optimise TAC, not AST | TAC exposes assignments, temporaries, and jumps directly, making constant folding and simple dead-code removal easier to implement and test. |
| Start with simple register allocation | A fixed temporary-register pool with stack spills is easier to verify than graph colouring and is sufficient for a toy compiler. |
| Use stack frames per function | Saving `$ra`, preserving required registers, and allocating local storage per call are necessary for nested and recursive functions. |
| Lower I/O through MIPS syscalls | MARS/SPIM syscalls provide a practical target for the required integer/character/string I/O without linking a C standard library. |
| Verify emitted code in a simulator | Text comparison alone cannot show whether calling convention, branches, and array addresses work at runtime. |
