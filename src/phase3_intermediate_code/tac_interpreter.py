#!/usr/bin/env python3
"""
TAC interpreter: loads an IR file and runs it, so the compiler's output can
be checked against gcc without a MIPS simulator.

    python3 tac_interpreter.py FILE.ir [args...] < input

Standalone on purpose (it imports nothing from the compiler), so Phase 4 can
use it as the reference for what the IR means.

Semantics (README section "IR semantics")
  * int is 32-bit two's complement with wrap-around, / truncates toward zero,
    % has the sign of the dividend, shifts use the low 5 bits of the count.
  * char is a signed 8-bit value. float is IEEE single precision: every
    float result is rounded through a 32-bit pack.
  * Scalars are named slots. Arrays and strings live in a flat byte memory;
    an array name stands for its base address, a `str` slot holds an address.
  * param pushes on a pending list; call f, n takes the last n values.
  * The IR is checked when it is loaded: undefined names or labels, wrong
    parameter counts and int/float mix-ups are reported as errors.
"""
import math
import re
import struct
import sys

MEM_SIZE = 8 * 1024 * 1024
DATA_BASE = 0x1000
MAX_DEPTH = 100000
DEFAULT_MAX_STEPS = 50_000_000

CLASS = {"int": "i", "char": "i", "float": "f", "str": "a"}
WIDTH = {"int": 4, "char": 1, "float": 4, "str": 4}

INTRINSICS = {              # name: (parameter classes, result class)
    "print_int": ("i", None), "print_char": ("i", None),
    "print_str": ("a", None), "print_float": ("f", None),
    "read_int": ("", "i"), "read_char": ("", "i"), "read_float": ("", "f"),
    "read_str": ("a", None), "atoi": ("a", "i"), "scan_status": ("", "i"),
}


class IRError(Exception):
    """The IR file is malformed or fails the load-time checks."""


class RunError(Exception):
    """A fault while the program runs."""


# ---------------------------------------------------------------------------
# number helpers
# ---------------------------------------------------------------------------
def wrap32(v: int) -> int:
    return (v + 2 ** 31) % 2 ** 32 - 2 ** 31


def f32(x: float) -> float:
    try:
        return struct.unpack("<f", struct.pack("<f", x))[0]
    except OverflowError:
        return math.inf if x > 0 else -math.inf


def idiv(a: int, b: int) -> int:
    if b == 0:
        raise RunError("division by zero")
    q = abs(a) // abs(b)
    return wrap32(q if (a < 0) == (b < 0) else -q)


def imod(a: int, b: int) -> int:
    if b == 0:
        raise RunError("division by zero")
    return wrap32(a - b * idiv(a, b))


def fdiv(a: float, b: float) -> float:
    if b != 0:
        return f32(a / b)
    if a == 0 or a != a:
        return math.nan
    return math.inf * math.copysign(1.0, a) * math.copysign(1.0, b)


def f2i(x: float) -> int:
    if x != x or abs(x) >= 2 ** 31:
        return -2 ** 31             # what x86 gives for out-of-range values
    return int(x)


def i2c(v: int) -> int:
    return ((v & 0xFF) ^ 0x80) - 0x80


INT_FN = {
    "+": lambda a, b: wrap32(a + b), "-": lambda a, b: wrap32(a - b),
    "*": lambda a, b: wrap32(a * b), "/": idiv, "%": imod,
    "&": lambda a, b: a & b, "|": lambda a, b: a | b, "^": lambda a, b: a ^ b,
    "<<": lambda a, b: wrap32(a << (b & 31)), ">>": lambda a, b: a >> (b & 31),
    "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b),
    "<": lambda a, b: int(a < b), "<=": lambda a, b: int(a <= b),
    ">": lambda a, b: int(a > b), ">=": lambda a, b: int(a >= b),
}
FLOAT_ARITH_FN = {
    "+f": lambda a, b: f32(a + b), "-f": lambda a, b: f32(a - b),
    "*f": lambda a, b: f32(a * b), "/f": fdiv,
}
FLOAT_CMP_FN = {
    "==f": lambda a, b: int(a == b), "!=f": lambda a, b: int(a != b),
    "<f": lambda a, b: int(a < b), "<=f": lambda a, b: int(a <= b),
    ">f": lambda a, b: int(a > b), ">=f": lambda a, b: int(a >= b),
}
UNARY = {                   # text: (function, operand class, result class)
    "-": (lambda a: wrap32(-a), "i", "i"),
    "~": (lambda a: ~a, "i", "i"),
    "!": (lambda a: int(a == 0), "i", "i"),
    "-f": (lambda a: -a, "f", "f"),
    "i2f": (lambda a: f32(float(a)), "i", "f"),
    "f2i": (f2i, "f", "i"),
    "i2c": (i2c, "i", "i"),
}


# ---------------------------------------------------------------------------
# reading the file
# ---------------------------------------------------------------------------
INT_RE = re.compile(r"^[+-]?\d+$")
FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")
NAME = r"[A-Za-z_][\w.]*"
TYPE = r"(?:int|char|float|str)"


def unescape(text: str) -> bytes:
    out = bytearray()
    i = 0
    simple = {"n": 10, "t": 9, "r": 13, "0": 0, '"': 34, "\\": 92}
    while i < len(text):
        c = text[i]
        if c != "\\":
            out += c.encode("utf-8")
            i += 1
            continue
        i += 1
        if i >= len(text):
            raise IRError("string ends with a backslash")
        e = text[i]
        if e == "x":
            out.append(int(text[i + 1:i + 3], 16))
            i += 3
        elif e in simple:
            out.append(simple[e])
            i += 1
        else:
            raise IRError(f"unknown escape \\{e} in string")
    return bytes(out)


def parse_dims(text: str) -> tuple:
    return tuple(None if d == "" else int(d) for d in re.findall(r"\[(\d*)\]", text))


def parse_constant(tok: str):
    if INT_RE.match(tok):
        return int(tok)
    if FLOAT_RE.match(tok):
        return f32(float(tok))
    return None


class Function:
    def __init__(self, name, params, ret):
        self.name = name
        self.params = params        # [(type, name, dims)]
        self.ret = ret
        self.locals = []            # [(type, name, dims)]
        self.temps = {}             # name -> type
        self.lines = []             # (line number, text) of instructions
        self.code = []              # linked instructions
        self.labels = {}
        self.arrays = []            # [(name, bytes)] locals that need memory
        self.initial = {}


class Program:
    def __init__(self):
        self.strings = []           # (label, bytes)
        self.globals = []           # (name, type, dims, init text)
        self.functions = {}


def parse_ir(text: str) -> Program:
    prog = Program()
    section = None
    func = None
    for no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if line == ".data":
                section = "data"
            elif line == ".text":
                section = "text"
            elif section == "data":
                parse_data_line(prog, line)
            elif section == "text":
                func = parse_text_line(prog, func, line, no)
            else:
                raise IRError("expected .data or .text")
        except IRError as exc:
            raise IRError(f"line {no}: {exc}") from None
    if func is not None:
        raise IRError("missing endfunc at the end of the file")
    return prog


def parse_data_line(prog: Program, line: str) -> None:
    m = re.match(rf'^({NAME})\s*:\s*"(.*)"$', line)
    if m:
        prog.strings.append((m.group(1), unescape(m.group(2))))
        return
    m = re.match(rf"^global\s+({NAME})\s*:\s*({TYPE})((?:\[\d+\])*)\s*(?:=\s*(.+))?$", line)
    if m:
        prog.globals.append((m.group(1), m.group(2), parse_dims(m.group(3)), m.group(4)))
        return
    raise IRError(f"cannot read data line: {line}")


def parse_text_line(prog: Program, func, line: str, no: int):
    if func is None:
        m = re.match(rf"^func\s+({NAME})\s*\((.*)\)\s*:\s*({TYPE}|void)$", line)
        if not m:
            raise IRError(f"expected a func header, got: {line}")
        params = []
        for part in [p.strip() for p in m.group(2).split(",") if p.strip()]:
            pm = re.match(rf"^({TYPE})\s+({NAME})((?:\[\d*\])*)$", part)
            if not pm:
                raise IRError(f"bad parameter: {part}")
            params.append((pm.group(1), pm.group(2), parse_dims(pm.group(3))))
        if m.group(1) in prog.functions:
            raise IRError(f"function {m.group(1)} defined twice")
        func = Function(m.group(1), params, m.group(3))
        prog.functions[func.name] = func
        return func
    if line == "endfunc":
        return None
    m = re.match(rf"^local\s+({TYPE})\s+({NAME})((?:\[\d+\])*)$", line)
    if m and not func.lines:
        func.locals.append((m.group(1), m.group(2), parse_dims(m.group(3))))
        return func
    m = re.match(rf"^temp\s+(.+)$", line)
    if m and not func.lines and not re.match(r"^temp\s*=", line):
        for part in m.group(1).split(","):
            tm = re.match(rf"^\s*({NAME})\s*:\s*({TYPE})\s*$", part)
            if not tm:
                raise IRError(f"bad temp declaration: {part.strip()}")
            func.temps[tm.group(1)] = tm.group(2)
        return func
    func.lines.append((no, line))
    return func


# ---------------------------------------------------------------------------
# linking: resolve names, check classes, build executable tuples
# ---------------------------------------------------------------------------
# opcodes
COPY, BIN, UN, GOTO, IFJ, LOAD, STORE, PARAM, CALL, RET = range(10)


class Linker:
    def __init__(self, prog: Program):
        self.prog = prog
        self.str_names = {label for label, _ in prog.strings}
        self.gtype = {}             # global name -> (type, dims)
        for name, t, dims, _ in prog.globals:
            if name in self.gtype or name in self.str_names:
                raise IRError(f"global {name} defined twice")
            self.gtype[name] = (t, dims)

    def link(self) -> None:
        for func in self.prog.functions.values():
            self.link_function(func)

    # name information ------------------------------------------------------
    def declare(self, func: Function) -> None:
        self.info = {}              # name -> (type, dims)
        for t, name, dims in func.params + func.locals:
            self.add(name, t, dims)
        for name, t in func.temps.items():
            self.add(name, t, ())

    def add(self, name, t, dims) -> None:
        if name in self.info:
            raise IRError(f"{name} declared twice in one function")
        self.info[name] = (t, dims)

    def lookup(self, name):
        if name in self.info:
            return "l", self.info[name]
        if name in self.gtype:
            return "g", self.gtype[name]
        return None, None

    def operand(self, tok: str):
        """(kind, value, class): kind c = constant, l = local, g = global."""
        value = parse_constant(tok)
        if value is not None:
            return ("c", value, "f" if isinstance(value, float) else "i")
        kind, info = self.lookup(tok)
        if kind is not None:
            t, dims = info
            return (kind, tok, "a" if dims else CLASS[t])
        if tok in self.str_names:
            return ("s", tok, "a")
        raise IRError(f"undefined name {tok}")

    def destination(self, tok: str):
        kind, info = self.lookup(tok)
        if kind is None:
            raise IRError(f"undefined name {tok}")
        t, dims = info
        if dims:
            raise IRError(f"cannot assign to array {tok}")
        return (kind, tok, CLASS[t])

    def base(self, tok: str):
        """An array name or a str slot used as the base of x[off]."""
        kind, info = self.lookup(tok)
        if kind is None:
            raise IRError(f"undefined name {tok}")
        t, dims = info
        if dims:
            elem = t
        elif t == "str":
            elem = "char"
        else:
            raise IRError(f"{tok} is not an array or string")
        return (kind, tok, "a"), elem

    # one function -----------------------------------------------------------
    def link_function(self, func: Function) -> None:
        self.declare(func)
        for t, name, dims in func.locals:
            if dims:
                size = WIDTH[t]
                for d in dims:
                    size *= d
                func.arrays.append((name, size))
        for t, name, dims in func.params + func.locals:
            if not dims:
                func.initial[name] = 0.0 if t == "float" else 0
        for name, t in func.temps.items():
            func.initial[name] = 0.0 if t == "float" else 0
        # pass 1: labels
        index = 0
        for no, line in func.lines:
            m = re.match(rf"^({NAME}):$", line)
            if m:
                if m.group(1) in func.labels:
                    raise IRError(f"line {no}: label {m.group(1)} defined twice")
                func.labels[m.group(1)] = index
            else:
                index += 1
        # pass 2: instructions
        pending = []
        for no, line in func.lines:
            if re.match(rf"^({NAME}):$", line):
                pending = []
                continue
            try:
                func.code.append(self.instruction(func, line, pending))
            except IRError as exc:
                raise IRError(f"line {no} ({func.name}): {exc}") from None
        if pending:
            raise IRError(f"{func.name}: param without a call at the end")

    def target(self, func, label: str) -> int:
        if label not in func.labels:
            raise IRError(f"undefined label {label}")
        return func.labels[label]

    def instruction(self, func, line: str, pending: list):
        m = re.match(rf"^goto\s+({NAME})$", line)
        if m:
            return (GOTO, self.target(func, m.group(1)))
        m = re.match(rf"^if\s+(\S+)\s+(\S+)\s+(\S+)\s+goto\s+({NAME})$", line)
        if m:
            a, rel, b, label = m.groups()
            return self.conditional(func, a, rel, b, label)
        m = re.match(r"^param\s+(\S+)$", line)
        if m:
            o = self.operand(m.group(1))
            pending.append(o[2])
            return (PARAM, o)
        m = re.match(r"^return(?:\s+(\S+))?$", line)
        if m:
            return self.ret(func, m.group(1))
        m = re.match(rf"^(?:({NAME})\s*=\s*)?call\s+({NAME})\s*,\s*(\d+)$", line)
        if m:
            return self.call(pending, m.group(1), m.group(2), int(m.group(3)))
        m = re.match(rf"^({NAME})\[(\S+)\]\s*=\s*(\S+)$", line)
        if m:
            return self.store(*m.groups())
        m = re.match(rf"^({NAME})\s*=\s*({NAME})\[(\S+)\]$", line)
        if m:
            return self.load(*m.groups())
        m = re.match(rf"^({NAME})\s*=\s*(.+)$", line)
        if m:
            return self.assignment(m.group(1), m.group(2).split())
        raise IRError(f"cannot read instruction: {line}")

    def conditional(self, func, a, rel, b, label):
        oa, ob = self.operand(a), self.operand(b)
        if rel in INT_FN and rel in ("==", "!=", "<", "<=", ">", ">="):
            fn, cls = INT_FN[rel], "i"
        elif rel in FLOAT_CMP_FN:
            fn, cls = FLOAT_CMP_FN[rel], "f"
        else:
            raise IRError(f"unknown comparison {rel}")
        self.need(oa, cls, rel)
        self.need(ob, cls, rel)
        return (IFJ, fn, oa, ob, self.target(func, label))

    def need(self, o, cls, what):
        if o[2] != cls:
            names = {"i": "int", "f": "float", "a": "address"}
            raise IRError(f"operand {o[1]} is {names[o[2]]}, but {what} needs {names[cls]}")

    def ret(self, func, tok):
        want = None if func.ret == "void" else CLASS[func.ret]
        if tok is None:
            if want is not None:
                raise IRError(f"{func.name} must return a value")
            return (RET, None)
        o = self.operand(tok)
        if want is None:
            raise IRError(f"{func.name} is void but returns a value")
        self.need(o, want, "return")
        return (RET, o)

    def call(self, pending, dest, name, n):
        if name in INTRINSICS:
            pcls, rcls = INTRINSICS[name]
            plist = list(pcls)
        elif name in self.prog.functions:
            callee = self.prog.functions[name]
            plist = ["a" if dims else CLASS[t] for t, _, dims in callee.params]
            rcls = None if callee.ret == "void" else CLASS[callee.ret]
        else:
            raise IRError(f"call to undefined function {name}")
        if n != len(plist):
            raise IRError(f"{name} takes {len(plist)} parameter(s), call says {n}")
        if len(pending) < n:
            raise IRError(f"call {name}, {n} has only {len(pending)} param(s) before it")
        given = pending[len(pending) - n:]
        del pending[len(pending) - n:]
        for k, (g, w) in enumerate(zip(given, plist), start=1):
            if g != w:
                raise IRError(f"argument {k} of {name} has the wrong type")
        d = None
        if dest is not None:
            if rcls is None:
                raise IRError(f"{name} returns no value")
            d = self.destination(dest)
            self.need(d, rcls, "the result of the call")
        return (CALL, d, name, n)

    def load(self, dest, base, off):
        d = self.destination(dest)
        b, elem = self.base(base)
        o = self.operand(off)
        self.need(o, "i", "an array offset")
        self.need(d, CLASS[elem], "a load")
        return (LOAD, d, b, o, elem)

    def store(self, base, off, value):
        b, elem = self.base(base)
        o = self.operand(off)
        v = self.operand(value)
        self.need(o, "i", "an array offset")
        self.need(v, CLASS[elem], "a store")
        return (STORE, b, o, v, elem)

    def assignment(self, dest, rhs):
        d = self.destination(dest)
        if len(rhs) == 1:
            o = self.operand(rhs[0])
            self.need(o, d[2], "a copy")
            return (COPY, d, o)
        if len(rhs) == 2:
            op, tok = rhs
            if op not in UNARY:
                raise IRError(f"unknown unary operator {op}")
            fn, in_cls, out_cls = UNARY[op]
            o = self.operand(tok)
            self.need(o, in_cls, op)
            self.need(d, out_cls, f"the result of {op}")
            return (UN, d, fn, o)
        if len(rhs) == 3:
            ta, op, tb = rhs
            a, b = self.operand(ta), self.operand(tb)
            if op in INT_FN:
                fn, in_cls, out_cls = INT_FN[op], "i", "i"
            elif op in FLOAT_ARITH_FN:
                fn, in_cls, out_cls = FLOAT_ARITH_FN[op], "f", "f"
            elif op in FLOAT_CMP_FN:
                fn, in_cls, out_cls = FLOAT_CMP_FN[op], "f", "i"
            else:
                raise IRError(f"unknown operator {op}")
            self.need(a, in_cls, op)
            self.need(b, in_cls, op)
            self.need(d, out_cls, f"the result of {op}")
            return (BIN, d, fn, a, b)
        raise IRError(f"cannot read right-hand side: {' '.join(rhs)}")


# ---------------------------------------------------------------------------
# running
# ---------------------------------------------------------------------------
class Machine:
    def __init__(self, prog: Program, args, stdin, max_steps: int):
        self.prog = prog
        self.mem = bytearray(MEM_SIZE)
        self.out = bytearray()
        self.stdin = stdin          # bytes, or None to read sys.stdin lazily
        self.in_pos = 0
        self.max_steps = max_steps
        self.glob = {}
        self.sp = DATA_BASE
        self.pending = []
        self.layout_data(args)

    # memory -----------------------------------------------------------------
    def alloc(self, size: int) -> int:
        addr = self.sp
        self.sp += (size + 3) // 4 * 4
        if self.sp > MEM_SIZE:
            raise RunError("out of memory (stack overflow)")
        return addr

    def check(self, addr: int, width: int) -> None:
        if addr < DATA_BASE or addr + width > MEM_SIZE:
            raise RunError(f"memory access at address {addr} is out of range")

    def load_mem(self, addr: int, kind: str):
        self.check(addr, WIDTH[kind])
        if kind == "char":
            return i2c(self.mem[addr])
        if kind == "int":
            return struct.unpack_from("<i", self.mem, addr)[0]
        if kind == "str":
            return struct.unpack_from("<I", self.mem, addr)[0]
        return struct.unpack_from("<f", self.mem, addr)[0]

    def store_mem(self, addr: int, kind: str, v) -> None:
        self.check(addr, WIDTH[kind])
        if kind == "char":
            self.mem[addr] = v & 0xFF
        elif kind == "int":
            struct.pack_into("<i", self.mem, addr, v)
        elif kind == "str":
            struct.pack_into("<I", self.mem, addr, v & 0xFFFFFFFF)
        else:
            struct.pack_into("<f", self.mem, addr, v)

    def put_bytes(self, data: bytes) -> int:
        addr = self.alloc(len(data) + 1)
        self.mem[addr:addr + len(data)] = data
        self.mem[addr + len(data)] = 0
        return addr

    def cstring(self, addr: int) -> bytes:
        end = addr
        while True:
            self.check(end, 1)
            if self.mem[end] == 0:
                return bytes(self.mem[addr:end])
            end += 1

    def layout_data(self, args) -> None:
        self.str_addr = {}
        for label, data in self.prog.strings:
            self.str_addr[label] = self.put_bytes(data)
        for name, t, dims, init in self.prog.globals:
            if dims:
                size = WIDTH[t]
                for d in dims:
                    size *= d
                addr = self.alloc(size)
                self.glob[name] = addr
                if init:
                    self.fill_array(addr, t, init)
            elif t == "float":
                self.glob[name] = self.const_init(init, 0.0)
            else:
                self.glob[name] = self.const_init(init, 0)
        ptrs = [self.put_bytes(a.encode("utf-8")) for a in args]
        self.argv = self.alloc(4 * max(1, len(ptrs)))
        for k, p in enumerate(ptrs):
            self.store_mem(self.argv + 4 * k, "str", p)
        self.argc = len(ptrs)

    def const_init(self, text, default):
        if text is None:
            return default
        text = text.strip()
        if text in self.str_addr:
            return self.str_addr[text]
        v = parse_constant(text)
        if v is None:
            raise IRError(f"bad initial value {text}")
        return v

    def fill_array(self, addr: int, t: str, init: str) -> None:
        body = init.strip()
        if not (body.startswith("{") and body.endswith("}")):
            raise IRError("array initializer must be in braces")
        values = [v.strip() for v in body[1:-1].split(",") if v.strip()]
        for k, v in enumerate(values):
            self.store_mem(addr + k * WIDTH[t], t, self.const_init(v, 0))

    # input and output ---------------------------------------------------------
    def input_bytes(self) -> bytes:
        if self.stdin is None:
            self.stdin = sys.stdin.buffer.read()
        return self.stdin

    def skip_space(self) -> None:
        data = self.input_bytes()
        while self.in_pos < len(data) and data[self.in_pos] in b" \t\n\r\f\v":
            self.in_pos += 1

    def token(self) -> bytes:
        self.skip_space()
        data = self.input_bytes()
        start = self.in_pos
        while self.in_pos < len(data) and data[self.in_pos] not in b" \t\n\r\f\v":
            self.in_pos += 1
        return data[start:self.in_pos]

    status = 0      # result of the last read_*: 0 ok, 1 text did not match, 2 end of input

    def fail_status(self) -> int:
        """Set and return the failure status after skipping white space."""
        self.status = 2 if self.in_pos >= len(self.input_bytes()) else 1
        return self.status

    def read_int(self) -> int:
        self.skip_space()
        m = re.compile(rb"[+-]?\d+").match(self.input_bytes(), self.in_pos)
        if not m:
            self.fail_status()
            return 0
        self.in_pos = m.end()
        self.status = 0
        return wrap32(int(m.group()))

    def read_float(self) -> float:
        self.skip_space()
        m = re.compile(rb"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?").match(
            self.input_bytes(), self.in_pos)
        if not m:
            self.fail_status()
            return 0.0
        self.in_pos = m.end()
        self.status = 0
        return f32(float(m.group()))

    def read_char(self) -> int:
        data = self.input_bytes()
        if self.in_pos >= len(data):
            self.status = 2
            return -1
        c = data[self.in_pos]
        self.in_pos += 1
        self.status = 0
        return i2c(c)

    def intrinsic(self, name: str, a: list):
        if name == "print_int":
            self.out += str(a[0]).encode()
        elif name == "print_char":
            self.out.append(a[0] & 0xFF)
        elif name == "print_str":
            self.out += self.cstring(a[0])
        elif name == "print_float":
            self.out += ("%f" % a[0]).encode()
        elif name == "read_int":
            return self.read_int()
        elif name == "read_char":
            return self.read_char()
        elif name == "read_float":
            return self.read_float()
        elif name == "read_str":
            word = self.token()
            self.status = 0 if word else 2
            self.check(a[0], len(word) + 1)
            self.mem[a[0]:a[0] + len(word)] = word
            self.mem[a[0] + len(word)] = 0
        elif name == "scan_status":
            return self.status
        elif name == "atoi":
            m = re.match(rb"\s*[+-]?\d+", self.cstring(a[0]))
            return wrap32(int(m.group())) if m else 0
        return None

    # frames -------------------------------------------------------------------
    def new_frame(self, func: Function, args: list) -> dict:
        fr = dict(func.initial)
        for (t, name, dims), v in zip(func.params, args):
            fr[name] = v
        for name, size in func.arrays:
            addr = self.alloc(size)
            self.mem[addr:addr + size] = bytes(size)
            fr[name] = addr
        return fr

    def run(self):
        main = self.prog.functions.get("main")
        if main is None:
            raise IRError("no main function")
        if len(main.params) == 2:
            args = [self.argc, self.argv]
        elif not main.params:
            args = []
        else:
            raise IRError("main must take no parameters or (int argc, str argv[])")
        glob = self.glob
        stack = []
        func = main
        sp0 = self.sp
        fr = self.new_frame(func, args)
        code, pc, steps = func.code, 0, 0
        dest = None
        result = 0

        def get(o, fr):
            k = o[0]
            if k == "c":
                return o[1]
            if k == "l":
                return fr[o[1]]
            if k == "g":
                return glob[o[1]]
            return self.str_addr[o[1]]

        def put(d, fr, v):
            if d[0] == "l":
                fr[d[1]] = v
            else:
                glob[d[1]] = v

        while True:
            if pc >= len(code):
                raise RunError(f"control reaches the end of {func.name} without a return")
            steps += 1
            if steps > self.max_steps:
                raise RunError("step limit exceeded (infinite loop?)")
            ins = code[pc]
            pc += 1
            op = ins[0]
            if op == COPY:
                put(ins[1], fr, get(ins[2], fr))
            elif op == BIN:
                put(ins[1], fr, ins[2](get(ins[3], fr), get(ins[4], fr)))
            elif op == UN:
                put(ins[1], fr, ins[2](get(ins[3], fr)))
            elif op == GOTO:
                pc = ins[1]
            elif op == IFJ:
                if ins[1](get(ins[2], fr), get(ins[3], fr)):
                    pc = ins[4]
            elif op == LOAD:
                addr = get(ins[2], fr) + get(ins[3], fr)
                put(ins[1], fr, self.load_mem(addr, ins[4]))
            elif op == STORE:
                addr = get(ins[1], fr) + get(ins[2], fr)
                self.store_mem(addr, ins[4], get(ins[3], fr))
            elif op == PARAM:
                self.pending.append(get(ins[1], fr))
            elif op == CALL:
                name, n = ins[2], ins[3]
                args = self.pending[len(self.pending) - n:]
                del self.pending[len(self.pending) - n:]
                if name in INTRINSICS:
                    value = self.intrinsic(name, args)
                    if ins[1] is not None:
                        put(ins[1], fr, value)
                else:
                    if len(stack) >= MAX_DEPTH:
                        raise RunError("call stack too deep (infinite recursion?)")
                    stack.append((func, pc, fr, ins[1], self.sp))
                    func = self.prog.functions[name]
                    code, pc = func.code, 0
                    fr = self.new_frame(func, args)
            else:  # RET
                value = get(ins[1], fr) if ins[1] is not None else None
                if not stack:
                    result = value if value is not None else 0
                    break
                func, pc, caller_fr, dest, self.sp = stack.pop()
                code = func.code
                if dest is not None:
                    put(dest, caller_fr, value)
                fr = caller_fr
        self.sp = sp0
        return result


def run_ir(text: str, args=(), stdin=b"", max_steps: int = DEFAULT_MAX_STEPS):
    """Run IR text. Returns (output bytes, exit code). Raises IRError for a
    bad file and RunError for a fault while running."""
    prog = parse_ir(text)
    Linker(prog).link()
    machine = Machine(prog, ["a.out"] + list(args), stdin, max_steps)
    value = machine.run()
    return bytes(machine.out), value & 0xFF if isinstance(value, int) else 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    max_steps = DEFAULT_MAX_STEPS
    if argv and argv[0].startswith("--max-steps="):
        max_steps = int(argv.pop(0).split("=", 1)[1])
    if not argv:
        print("usage: tac_interpreter.py [--max-steps=N] FILE.ir [args...]", file=sys.stderr)
        return 125
    path, args = argv[0], argv[1:]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 125
    machine = None
    try:
        prog = parse_ir(text)
        Linker(prog).link()
        machine = Machine(prog, [path] + args, None, max_steps)
        value = machine.run()
    except (IRError, RunError) as exc:
        if machine is not None:
            sys.stdout.buffer.write(bytes(machine.out))
            sys.stdout.buffer.flush()
        kind = "runtime error" if isinstance(exc, RunError) else "IR error"
        print(f"{kind}: {exc}", file=sys.stderr)
        return 125
    sys.stdout.buffer.write(bytes(machine.out))
    sys.stdout.buffer.flush()
    return value & 0xFF if isinstance(value, int) else 0


if __name__ == "__main__":
    sys.exit(main())
