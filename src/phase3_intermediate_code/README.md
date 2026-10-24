# Phase 3: Meaning check and three-address code (the IR file)

**Job:** (1) check the meaning of the program: names declared, types match, calls have the right arguments;
(2) turn the tree into **three-address code (TAC)**: very simple instructions where each line does one thing,
like `t3 = t1 + t2`. The result is written to an *IR file* (IR = intermediate representation).

```
C source -> lexer -> parser (tree) -> semantic_analyzer (checked tree + symbol table)
         -> ir_generator (instructions) -> tac.py (text) -> prog.ir
prog.ir  -> tac_interpreter.py (runs it, to test the compiler)
```

| File | What it does |
| --- | --- |
| `type_system.py` | the types: `int`, `char`, `float`, `void`, strings (`char *`), arrays, functions |
| `symbol_table.py` | a table of names with nested scopes; gives shadowed names unique IR names (`x`, `x.1`, `x.2`), sizes and frame offsets |
| `semantic_analyzer.py` | all checks, constant folding (`2*3` becomes `6`), notes added to the tree |
| `tac.py` | the instruction object and the printer for the IR file |
| `ir_generator.py` | tree to instructions |
| `tac_interpreter.py` | loads an IR file, checks it, runs it. It is the exact definition of what each instruction means |

**Use it**
```
bin/tacgen prog.c -o prog.ir         write the IR file          (--tac prints it instead)
bin/tacgen prog.c --semantic         print the symbol table with sizes and offsets
python3 src/phase3_intermediate_code/tac_interpreter.py prog.ir [args] < input.txt
```
Any error: messages on the error stream, exit code 1, no IR file written.

## Supported language
- Types: `int` (4 bytes), `char` (1 byte, signed), `float` (4 bytes); `double` = `float`; `short long signed unsigned` = `int`; `bool` is its own type whose value is always 0 or 1.
  `char *` works as a string (literals, `argv[i]`, `atoi`, `%s`, indexing) but there is no pointer arithmetic.
- Everything in the top-level README feature list. `main` may be `main()`, `main(void)` or `main(int argc, char *argv[])`.
- `printf`/`scanf` formats must be string literals using only `%d %i %c %f %s %%` (no width or precision).
- Names must be declared before use (prototypes are fine). `static` is accepted on globals and functions. `extern int x;` may be followed by the definition `int x = 1;`.
- A user function may be called `print_int`, `read_int` and so on; in the IR it is written `print_int.u` so it cannot clash with the built-in of the same name. (`printf`, `scanf`, `atoi` cannot be redefined.)
- Not supported (clear error `unsupported feature: ...`): pointers except `char *`, `&` outside `scanf`, `struct`, `union`,
  classes (constructors, `Class::method`, `this`), lambdas, `auto`, references, function pointers, `new/delete`, `malloc`/`free`, file I/O, variadic functions, `static` locals.

## Checks that are reported (each has a test in `test/phase3_tac/invalid`)
undeclared name; name declared twice; unknown function; wrong number or type of arguments; wrong return type, missing or extra
return value; `break`/`continue` outside a loop; `goto` to a missing label; duplicate label; too many subscripts or subscript on a
non-array; non-integer index; assigning to an array, a `const` or a non-variable; using a `void` value; bad array size;
duplicate `case`/`default`; missing or malformed `main`; wrong `printf`/`scanf` format, count or types; division by constant zero;
use of a reserved name (`printf`, `scanf`, `atoi`); an `extern` variable that is never defined; every unsupported feature.
All errors in a file are collected and printed together, sorted by line.

## The IR file format
```
.data
str0: "sum = "                  a string (C escapes)
global g : int = 5              a global variable, optional constant value
global tbl : int[4] = {1,2,3,4} a global array
.text
func fact(int n) : int          name, parameters with types, return type (int char float str void)
    local int y                 a local variable
    local int a[3][4]           a local array
    temp t1:int, t2:int         every temporary with its type
    if n > 1 goto L1
    return 1
L1:
    t1 = n - 1
    param t1
    t2 = call fact, 1
    t3 = n * t2
    return t3
endfunc
```
`str` is a string handle (a 4-byte address). Array parameters are written `int a[]` or `int m[][3]`. Temporaries are `t1, t2...`
(restart in each function), labels `L1, L2...` (unique in the file), labels from `goto` are `L_<function>_<name>`.
Layout: labels at the left edge, instructions indented 4 spaces.

| Instruction | Meaning |
| --- | --- |
| `x = y` | copy (y may be a constant) |
| `x = y op z` | `+ - * / % & \| ^ << >> == != < <= > >=`; float forms `+f -f *f /f <f <=f >f >=f ==f !=f` |
| `x = - y`, `~ y`, `! y`, `-f y` | unary |
| `x = i2f y`, `f2i y`, `i2c y` | int to float, float to int, int to char (keep low 8 bits, sign-extend) |
| `goto L`, `if x relop y goto L`, `L:` | jumps and labels |
| `x = a[off]`, `a[off] = y` | array element at **byte** offset `off` (row-major: `a[i][j]` is offset `i*rowsize + j*elemsize`) |
| `param x`, `x = call f, n`, `call f, n`, `return`, `return y` | calls: all arguments are computed first, then one `param` each (left to right), then `call` |

### Built-in functions (called like normal functions)
`print_int print_char print_str print_float read_int read_char read_float read_str atoi scan_status`.
`printf` becomes one `print_*` call per piece (text pieces use `print_str`). `scanf` becomes, for each value:
`t = call read_int, 0`, then `s = call scan_status, 0` (0 = worked, 1 = text did not match, 2 = input ended), and the variable is
stored only if it worked; on failure `scanf` stops. So like C, a failed `scanf` leaves the variable unchanged, returns
the number of values read, and returns -1 if the input ended before the first value.

## How the code is generated (short)
- **Conditions** (`if`, loops, `&&`, `||`, `!`) are compiled to jumps to two labels, "true" and "false", chosen by the caller
  `&&` and `||` therefore skip their right side with no extra temporaries. No backpatching is used (it is the other
  textbook method: leave jump targets blank and fill them in later).
- **Loops** use labelled blocks; a stack of (break, continue) labels serves `break` and `continue`. `continue` in `for` jumps to the update part.
- **switch**: evaluate once, a chain of compare-and-jump, case bodies stay in order so fall-through works.
- **Arrays**: one `load`/`store` with a computed byte offset; constants are folded; `char` arrays use width 1.
- **Calls**: arguments evaluated first, then `param`s. Recursion needs nothing special.
- A function that does not end in `return` gets one added.

## What the interpreter does (the meaning of the IR)
- `int` is 32-bit and wraps around; `/` truncates toward zero; `%` has the sign of the left side; `>>` is arithmetic.
- `char` is signed 8-bit. `float` is single precision (every result rounded). `print_float` prints like `%f`.
- Memory is flat bytes; an array name is its base address. Uninitialised locals read as 0 (do not rely on this).
- It checks the IR when loading (unknown names/labels, wrong parameter counts or types) and when running (division by zero, bad
  addresses, endless loops after 50 million steps, endless recursion). Exit status is `main`'s return value; 125 for an IR error.

## Known limitations (kept on purpose)
- `short`, `long`, `unsigned` are 32-bit `int`; `double` is a 32-bit `float`.
- `scanf("%i")` reads decimal only, like `%d`.
- One row of a 2-D array cannot be passed (`f(m[1])`); whole arrays can.
- Array indexes out of range are not detected (undefined in C too); keep tests in range.
- `float * 0.1` : gcc calculates in double precision, we round every float operation, so a non-exact decimal such as `0.1`
  mixed into float math can differ in the last digit.
- Argument evaluation order is left to right (C leaves it open); tests must not depend on it.
- `printf` cannot be used as a value.

## For Phase 4 (not started)
The `.ir` file has everything needed: data section, locals with types, a type for every temporary.
Frame layout (see `--semantic`): parameters first, then locals in declaration order, each rounded up to 4 bytes;
temporaries are not in the frame size. Suggested MIPS system calls: `print_int` 1, `print_float` 2, `print_str` 4, `read_int` 5,
`read_float` 6, `read_str` 8, `print_char` 11, `read_char` 12, exit 10. `atoi` and `scan_status` have no system call (write them in
a small runtime routine; `scan_status` needs the reading routines to remember whether the last read worked).
Syscall 8 reads a whole line while `read_str` here reads one word; trim it. Check every Phase 4 result against the interpreter
and `test/phase3_tac/valid/**/*.expected`.
