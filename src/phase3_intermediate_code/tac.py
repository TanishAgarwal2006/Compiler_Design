"""
Three-address code.

Every instruction is a quadruple (op, arg1, arg2, result), kept as a small
Python object and printed as one line of readable text. This module holds

  * Instr and the opcode tables,
  * the IR module classes (strings, globals, functions with locals and temps),
  * the temp and label name generators,
  * the formatter that writes the IR file (layout in the phase 3 README).

Operands are plain Python values: a str is a variable, temp or string label,
an int or float is a constant.

Opcodes
    copy                  result = arg1
    + - * / % & | ^ << >> == != < <= > >=      result = arg1 op arg2
    +f -f *f /f ==f !=f <f <=f >f >=f          float versions
    neg compl not negf    result = - arg1, ~ arg1, ! arg1, -f arg1
    i2f f2i i2c           conversions
    goto                  goto result
    if<  if==  if<f ...   if arg1 relop arg2 goto result
    label                 result:
    load                  result = arg1[arg2]     (arg2 is a byte offset)
    store                 result[arg2] = arg1
    param                 param arg1
    call                  result = call arg1, arg2   (result may be None)
    return                return arg1                (arg1 may be None)
"""
import struct
from dataclasses import dataclass, field
from typing import Optional

INT_BINARY = ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>",
              "==", "!=", "<", "<=", ">", ">="]
FLOAT_BINARY = ["+f", "-f", "*f", "/f", "==f", "!=f", "<f", "<=f", ">f", ">=f"]
BINARY_OPS = set(INT_BINARY) | set(FLOAT_BINARY)
RELOPS = ["==", "!=", "<", "<=", ">", ">=",
          "==f", "!=f", "<f", "<=f", ">f", ">=f"]

# internal opcode -> text used in the IR file
UNARY_TEXT = {"neg": "-", "compl": "~", "not": "!", "negf": "-f",
              "i2f": "i2f", "f2i": "f2i", "i2c": "i2c"}
UNARY_OPS = set(UNARY_TEXT)
UNARY_FROM_TEXT = {v: k for k, v in UNARY_TEXT.items()}


@dataclass
class Instr:
    op: str
    arg1: object = None
    arg2: object = None
    result: object = None


def is_cond_jump(op: str) -> bool:
    return op.startswith("if") and op[2:] in RELOPS


# ---------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------
def to_f32(x: float) -> float:
    """Round a Python float to single precision."""
    try:
        return struct.unpack("<f", struct.pack("<f", x))[0]
    except OverflowError:
        return float("inf") if x > 0 else float("-inf")


def format_float(x: float) -> str:
    if x != x:
        raise ValueError("a NaN constant cannot be written to the IR")
    if x in (float("inf"), float("-inf")):
        return "1e999" if x > 0 else "-1e999"     # reads back as infinity
    text = repr(float(x))
    if "." not in text and "e" not in text:
        text += ".0"
    return text


def format_operand(x) -> str:
    if isinstance(x, float):
        return format_float(x)
    return str(x)


def escape_bytes(data: bytes) -> str:
    """Text form of a string for the data section (C style escapes)."""
    out = []
    for c in data:
        if c == 34:
            out.append('\\"')
        elif c == 92:
            out.append("\\\\")
        elif c == 10:
            out.append("\\n")
        elif c == 9:
            out.append("\\t")
        elif c == 13:
            out.append("\\r")
        elif 32 <= c < 127:
            out.append(chr(c))
        else:
            out.append(f"\\x{c:02x}")
    return "".join(out)


# ---------------------------------------------------------------------------
# IR module
# ---------------------------------------------------------------------------
@dataclass
class IRVar:
    name: str
    type: str            # int, char, float or str
    dims: tuple = ()     # array dimensions; the first may be None for a parameter


@dataclass
class IRGlobal:
    name: str
    type: str
    dims: tuple = ()
    init: object = None  # None, a constant, a string label, or a list of constants


@dataclass
class IRFunction:
    name: str
    params: list
    ret: str             # int, char, float, str or void
    locals: list = field(default_factory=list)
    temps: dict = field(default_factory=dict)    # name -> type, in creation order
    code: list = field(default_factory=list)


@dataclass
class IRModule:
    strings: list = field(default_factory=list)    # (label, bytes)
    globals: list = field(default_factory=list)
    functions: list = field(default_factory=list)


class TempGen:
    """Temps t1, t2, ... for one function. Names already used by variables
    are skipped so a source variable called t1 cannot clash."""

    def __init__(self, taken: set):
        self.taken = taken
        self.count = 0
        self.types = {}

    def new(self, type_name: str) -> str:
        while True:
            self.count += 1
            name = f"t{self.count}"
            if name not in self.taken:
                break
        self.types[name] = type_name
        return name


class LabelGen:
    """Labels L1, L2, ... unique over the whole file."""

    def __init__(self):
        self.count = 0

    def new(self) -> str:
        self.count += 1
        return f"L{self.count}"


# ---------------------------------------------------------------------------
# text output
# ---------------------------------------------------------------------------
def format_type(type_name: str, dims: tuple) -> str:
    return type_name + "".join(f"[{'' if d is None else d}]" for d in dims)


def format_instr(i: Instr) -> str:
    op, a, b, r = i.op, i.arg1, i.arg2, i.result
    fa, fb = format_operand(a), format_operand(b)
    if op == "copy":
        return f"{r} = {fa}"
    if op in BINARY_OPS:
        return f"{r} = {fa} {op} {fb}"
    if op in UNARY_OPS:
        return f"{r} = {UNARY_TEXT[op]} {fa}"
    if op == "goto":
        return f"goto {r}"
    if is_cond_jump(op):
        return f"if {fa} {op[2:]} {fb} goto {r}"
    if op == "label":
        return f"{r}:"
    if op == "load":
        return f"{r} = {fa}[{fb}]"
    if op == "store":
        return f"{r}[{fb}] = {fa}"
    if op == "param":
        return f"param {fa}"
    if op == "call":
        prefix = f"{r} = " if r is not None else ""
        return f"{prefix}call {a}, {b}"
    if op == "return":
        return "return" if a is None else f"return {fa}"
    raise ValueError(f"unknown opcode {op!r}")


def _global_line(g: IRGlobal) -> str:
    line = f"global {g.name} : {format_type(g.type, g.dims)}"
    if g.init is None:
        return line
    if isinstance(g.init, list):
        return line + " = {" + ",".join(format_operand(v) for v in g.init) + "}"
    return line + " = " + format_operand(g.init)


def _function_lines(f: IRFunction) -> list:
    params = ", ".join(f"{p.type} {p.name}" + format_type("", p.dims) for p in f.params)
    lines = [f"func {f.name}({params}) : {f.ret}"]
    for v in f.locals:
        lines.append(f"    local {v.type} {v.name}" + format_type("", v.dims))
    names = list(f.temps.items())
    for k in range(0, len(names), 8):
        group = ", ".join(f"{n}:{t}" for n, t in names[k:k + 8])
        lines.append(f"    temp {group}")
    for ins in f.code:
        text = format_instr(ins)
        lines.append(text if ins.op == "label" else "    " + text)
    lines.append("endfunc")
    return lines


def format_module(m: IRModule) -> str:
    lines = [".data"]
    for label, data in m.strings:
        lines.append(f'{label}: "{escape_bytes(data)}"')
    for g in m.globals:
        lines.append(_global_line(g))
    lines.append(".text")
    for f in m.functions:
        lines.extend(_function_lines(f))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
