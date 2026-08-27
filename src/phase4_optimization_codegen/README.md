# Phase 4: Optimization & MIPS Code Generation

This module is scaffolded for Phase 4 of the compiler pipeline: optimizing Three-Address Code (TAC) and emitting target **MIPS Assembly (`.s`)** code.

---

## 1. Planned Design & Specifications

### 1.1 Optimization Passes
- **Constant Folding:** Evaluate constant expressions at compile time (e.g., `t1 = 2 + 3` -> `t1 = 5`).
- **Constant Propagation:** Replace variable uses with known constant values.
- **Dead Code Elimination:** Remove unused temporaries and unreachable code blocks.
- **Peephole Optimization:** Eliminate redundant jump sequences and duplicate memory loads.

### 1.2 MIPS Target Code Generation
- **Register Allocation:** Map compiler temporaries (`t1`, `t2`) to MIPS registers (`$t0`–`$t9`, `$s0`–`$s7`) with stack spilling mechanism.
- **Stack Frame Management:** Manage function call frames, local variables, saved return addresses (`$ra`), and frame pointers (`$fp`) to support recursive function calls.
- **System Call Lowering:** Map `printf` and `scanf` calls to MIPS MARS/SPIM environment syscalls (`li $v0, 1`, `li $v0, 4`, `li $v0, 5`).

---

## 2. Planned Module Layout

- **`optimizer.py`**: Implementation of TAC optimization passes.
- **`mips_generator.py`**: TAC quadruple to MIPS assembly translator.
- **`register_allocator.py`**: Register allocation and stack frame layout manager.
- **`run_codegen.py`**: Standalone driver for Phase 4 MIPS target code generation.
