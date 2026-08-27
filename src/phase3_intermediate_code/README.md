# Phase 3: Intermediate Code Generation (TAC)

This module is scaffolded for Phase 3 of the compiler pipeline: translating the Abstract Syntax Tree (AST) generated in Phase 2 into **Three-Address Code (TAC)** quadruples.

---

## 1. Planned Design & Specifications

### TAC Quadruple Representation
Each intermediate statement will be represented as a quadruple `(operator, arg1, arg2, result)`:

- **Arithmetic & Logical Quadruples:** `(+, a, b, t1)`, `(*, t1, c, t2)`
- **Temporary Allocator:** Sequence of compiler-generated temporary variables (`t1`, `t2`, `t3`, ...).
- **Label Generation:** Unique jump targets (`L1`, `L2`, `L3`, ...).
- **Control Flow Lowering:**
  - `if (condition)` -> `ifFalse condition goto L1`
  - `while` / `for` loops -> lowered to conditional jumps and loop labels.
  - `break` / `continue` -> resolved via active loop label stack.
- **Function Call Lowering:**
  - `param arg1`
  - `param arg2`
  - `call func_name, 2`
  - `return result`
- **Array Address Linearization:**
  - 1D Array: `offset = index * element_size`
  - Multi-Dimensional Array: Row-major order offset calculation `offset = (row * num_cols + col) * element_size`.

---

## 2. Planned Module Layout

- **`tac.py`**: Quadruple data structure and TAC string formatter.
- **`ir_generator.py`**: AST visitor class generating TAC sequences.
- **`run_tac.py`**: Standalone driver for Phase 3 intermediate code generation.
