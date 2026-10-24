"""
IR generation: annotated AST -> three-address code.

The semantic pass has already checked every type and stored the result on
the tree (ctype, const_value, symbol, ...), so this module only has to
walk the tree once and emit quadruples. Each expression visitor returns the
"place" that holds the value: a variable name, a temp, or a constant.

Rules used here
  * One operator per instruction. Constant sub-expressions were folded by the
    semantic pass, so they arrive as plain constants.
  * Assignment computes the value into a place first and then copies it
    (see the float example in the README), with i2f / f2i / i2c where the
    types differ. char is an int in the range -128..127: char -> int is free,
    int -> char needs i2c.
  * x++ as a value copies the old value to a temp first. As a statement it
    is the same as ++x.
  * Control flow: conditions are compiled by cond(e, T, F)
    into jumps to the inherited labels T (true) and F (false); && || ! only
    shuffle labels, so they short-circuit with no extra temps. No
    backpatching: the labels exist before the code that jumps to them.
    break/continue targets come from a stack of enclosing loops and switches.
  * Arrays: row-major, one explicit byte offset per access,
    offset = i1*stride1 + i2*stride2 + ... with stride = element width times
    the later dimensions; constant indices are folded into one constant.
    Elements are read with `load` and written with `store`; an array name
    used as a value is its base address. Initialisers become element stores
    (locals) or a constant list in the data section (globals).
  * printf is lowered to print_* intrinsic calls by walking the format items
    that the semantic pass produced.

Every feature of the handoff is implemented. Features that are deliberately
unsupported (see the phase 3 README) raise GenError or are rejected earlier by
the semantic pass, so a program that needs them fails with a clear message.
"""
from . import tac
from .tac import Instr, IRFunction, IRGlobal, IRModule, IRVar, to_f32
from math import prod

from .type_system import (
    INT, CHAR, FLOAT, BOOL, VOID, STRING, ArrayType, is_arithmetic,
)
from .semantic_analyzer import wrap32, wrap8

ARITH_OPS = {"+", "-", "*", "/"}
COMPARE_OPS = {"==", "!=", "<", "<=", ">", ">="}
COMPOUND_OPS = {
    "+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%",
    "&=": "&", "|=": "|", "^=": "^", "<<=": "<<", ">>=": ">>",
}
PRINT_INTRINSIC = {"d": "print_int", "c": "print_char", "f": "print_float", "s": "print_str"}


class GenError(Exception):
    """A construct the generator cannot translate."""

    def __init__(self, node, message: str):
        super().__init__(message)
        self.line = node if isinstance(node, int) else (getattr(node, "line", 0) or 0)
        self.message = message


class NotYetImplemented(GenError):
    def __init__(self, node, what: str, planned_for: str):
        super().__init__(node, f"not yet implemented: {what} (planned for {planned_for})")


def ir_type(t) -> str:
    """Name of a scalar type in the IR file."""
    if t == INT or t == BOOL:
        return "int"
    if t == CHAR:
        return "char"
    if t == FLOAT:
        return "float"
    if t == STRING:
        return "str"
    if t == VOID:
        return "void"
    raise GenError(0, f"no IR type for {t}")


def make_var(name: str, t) -> IRVar:
    if isinstance(t, ArrayType):
        return IRVar(name, ir_type(t.elem), tuple(t.dims))
    return IRVar(name, ir_type(t))


def const_convert(v, dst):
    """Convert a constant to type dst at compile time."""
    if dst == FLOAT:
        return to_f32(float(v))
    if dst == BOOL:
        return 1 if v else 0
    if isinstance(v, float):
        v = int(v) if v == v and abs(v) != float("inf") else -2 ** 31
    return wrap8(v) if dst == CHAR else wrap32(v)


class FunctionState:
    """Everything that belongs to the function being generated."""

    def __init__(self, name: str, ret, taken: set):
        self.name = name
        self.ret = ret
        self.code = []
        self.temps = tac.TempGen(taken)
        self.jumps = []            # (break_label, continue_label or None), innermost last


class IRGenerator:
    def __init__(self, result):
        self.result = result
        self.labels = tac.LabelGen()
        self.strings = {}          # bytes -> label, in first-use order
        self.fn = None
        self.reserved = self._all_names()

    def _all_names(self) -> set:
        names = set(self.result.table.global_scope.symbols)
        for info in self.result.functions.values():
            names |= info.used_names
        return names

    # --- entry point ------------------------------------------------------
    def generate(self, program) -> IRModule:
        module = IRModule()
        for decl in program.declarations:
            if decl.kind == "Declaration":
                self.global_declaration(decl, module)
            elif decl.kind == "FunctionDefinition":
                module.functions.append(self.function(decl))
        module.strings = [(label, data) for data, label in self.strings.items()]
        return module

    def string_label(self, data: bytes) -> str:
        if data not in self.strings:
            k = len(self.strings)
            while f"str{k}" in self.reserved:
                k += 1
            label = f"str{k}"
            self.reserved.add(label)
            self.strings[data] = label
        return self.strings[data]

    # --- globals ----------------------------------------------------------
    def global_declaration(self, decl, module) -> None:
        if decl.storage == "typedef":
            return
        for idecl in decl.declarators:
            sym = getattr(idecl, "symbol", None)
            if sym is None:          # prototype or enum-only declaration
                continue
            if decl.storage == "extern" and idecl.initializer is None:
                continue             # "extern int x;" - the definition emits the global
            t = sym.type
            init = None
            if isinstance(t, ArrayType):
                init = self.global_array_init(idecl, t)
            elif idecl.init_kind == "scalar":
                if t == STRING:
                    init = self.string_label(idecl.initializer.string_bytes)
                else:
                    init = const_convert(idecl.init_value, t)
            module.globals.append(IRGlobal(sym.ir_name, *self.var_type(t), init))

    def var_type(self, t):
        if isinstance(t, ArrayType):
            return ir_type(t.elem), tuple(t.dims)
        return ir_type(t), ()

    def global_array_init(self, idecl, t):
        """Dense list of constants (trailing zeros dropped), or None."""
        if idecl.init_kind not in ("array", "string"):
            return None
        values = [0.0 if t.elem == FLOAT else 0] * t.element_count()
        for i, e in idecl.init_elems:
            v = e if isinstance(e, int) else e.const_value
            values[i] = const_convert(v, t.elem)
        while values and values[-1] == 0:
            values.pop()
        return values or None

    # --- functions --------------------------------------------------------
    def function(self, fd) -> IRFunction:
        info = fd.info
        sym = info.symbol
        ret = sym.type.ret
        self.fn = FunctionState(sym.ir_name, ret, info.used_names)
        for item in fd.body.items:
            self.visit(item)
        code = self.fn.code
        if not code or code[-1].op != "return":
            # falling off the end: return 0 (or nothing for void)
            if ret == VOID:
                self.emit("return")
            else:
                self.emit("return", 0.0 if ret == FLOAT else 0)
        irf = IRFunction(
            name=sym.ir_name,
            params=[make_var(p.ir_name, p.type) for p in info.params],
            ret=ir_type(ret),
            locals=[make_var(v.ir_name, v.type) for v in info.locals],
            temps=self.fn.temps.types,
            code=code,
        )
        self.fn = None
        return irf

    # --- helpers ----------------------------------------------------------
    def emit(self, op, a=None, b=None, result=None) -> None:
        self.fn.code.append(Instr(op, a, b, result))

    def new_temp(self, t) -> str:
        return self.fn.temps.new(ir_type(t))

    def binary(self, op, a, b, result_type) -> str:
        t = self.new_temp(result_type)
        self.emit(op, a, b, t)
        return t

    def unary(self, op, a, result_type) -> str:
        t = self.new_temp(result_type)
        self.emit(op, a, None, t)
        return t

    def convert(self, v, src, dst):
        """Convert place v from type src to type dst, emitting code if needed."""
        if src == dst or dst not in (INT, CHAR, FLOAT, BOOL):
            return v
        if isinstance(v, (int, float)):
            return const_convert(v, dst)
        if dst == BOOL:                      # any non-zero value becomes 1
            return self.binary("!=f" if src == FLOAT else "!=", v, 0.0 if src == FLOAT else 0, INT)
        if dst == FLOAT:
            return self.unary("i2f", v, FLOAT)
        if src == FLOAT:
            v = self.unary("f2i", v, INT)
            if dst == INT:
                return v
        if dst == CHAR and src != CHAR:
            return self.unary("i2c", v, CHAR)
        return v                     # char -> int needs nothing

    def visit(self, n):
        handler = getattr(self, "visit_" + n.kind, None)
        if handler is None:
            raise GenError(n, f"cannot generate code for {n.kind}")
        return handler(n)

    def expr(self, n):
        """Place holding the value of expression n."""
        cv = getattr(n, "const_value", None)
        if cv is not None and is_arithmetic(n.ctype):
            return const_convert(cv, n.ctype)
        return self.visit(n)

    def effect(self, e) -> None:
        """Evaluate expression e only for its side effects."""
        if e.kind == "UnaryOp" and e.operator in ("++", "--"):
            self.incdec(e, False)
        elif e.kind == "BinaryOp" and e.operator == ",":
            self.effect(e.left)
            self.effect(e.right)
        elif e.kind == "FunctionCall":
            self.visit_FunctionCall(e, discard=True)
        else:
            self.expr(e)

    # ======================================================================
    # statements
    # ======================================================================
    def visit_CompoundStatement(self, n):
        for item in n.items:
            self.visit(item)

    def visit_ExpressionStatement(self, n):
        if n.expression is not None:
            self.effect(n.expression)

    def visit_Declaration(self, n):
        if n.storage == "typedef":
            return
        for idecl in n.declarators:
            sym = getattr(idecl, "symbol", None)
            if sym is None:
                continue
            kind = idecl.init_kind
            if kind == "none":
                continue
            if kind != "scalar":
                self.local_array_init(idecl, sym.type)
                continue
            init = idecl.initializer
            v = self.convert(self.expr(init), init.ctype, sym.type)
            self.emit("copy", v, None, sym.ir_name)

    def local_array_init(self, idecl, t) -> None:
        """Element stores for every element; C zero-fills what the list omits.
        ponytail: fully unrolled, so int a[1000] = {0} emits 1000 stores;
        add a loop if big initialised local arrays appear."""
        given = dict(idecl.init_elems)
        name = idecl.symbol.ir_name
        for i in range(t.element_count()):
            e = given.get(i, 0)
            if isinstance(e, int):
                v = const_convert(e, t.elem)
            else:
                v = self.convert(self.expr(e), e.ctype, t.elem)
            self.emit("store", v, i * t.elem.width, name)

    def visit_ReturnStatement(self, n):
        if n.value is None:
            self.emit("return")
            return
        v = self.convert(self.expr(n.value), n.value.ctype, self.fn.ret)
        self.emit("return", v)

    # control flow
    def new_label(self) -> str:
        return self.labels.new()

    def label(self, name: str) -> None:
        self.emit("label", None, None, name)

    def goto(self, name: str) -> None:
        self.emit("goto", None, None, name)

    def stmt(self, n) -> None:
        if n is not None:
            self.visit(n)

    def cond(self, n, t, f) -> None:
        """Jump to label t if expression n is true, else to label f."""
        cv = getattr(n, "const_value", None)
        if cv is not None and is_arithmetic(n.ctype):
            self.goto(t if cv != 0 else f)
        elif n.kind == "UnaryOp" and n.operator == "!":
            self.cond(n.operand, f, t)
        elif n.kind == "BinaryOp" and n.operator in ("&&", "||"):
            mid = self.new_label()
            if n.operator == "&&":
                self.cond(n.left, mid, f)
            else:
                self.cond(n.left, t, mid)
            self.label(mid)
            self.cond(n.right, t, f)
        elif n.kind == "BinaryOp" and n.operator in COMPARE_OPS:
            lt, rt = n.left.ctype, n.right.ctype
            a, b = self.expr(n.left), self.expr(n.right)
            op = n.operator
            if lt == FLOAT or rt == FLOAT:
                a, b, op = self.convert(a, lt, FLOAT), self.convert(b, rt, FLOAT), op + "f"
            self.emit("if" + op, a, b, t)
            self.goto(f)
        else:
            v = self.expr(n)
            if n.ctype == FLOAT:
                self.emit("if!=f", v, 0.0, t)
            else:
                self.emit("if!=", v, 0, t)
            self.goto(f)

    def visit_IfStatement(self, n):
        then, end = self.new_label(), self.new_label()
        els = self.new_label() if n.else_branch is not None else end
        self.cond(n.condition, then, els)
        self.label(then)
        self.stmt(n.then_branch)
        if n.else_branch is not None:
            self.goto(end)
            self.label(els)
            self.stmt(n.else_branch)
        self.label(end)

    def loop_body(self, body, brk, cont) -> None:
        self.fn.jumps.append((brk, cont))
        self.stmt(body)
        self.fn.jumps.pop()

    def while_loop(self, n, negate: bool) -> None:
        test, body, end = self.new_label(), self.new_label(), self.new_label()
        self.label(test)
        self.cond(n.condition, *((end, body) if negate else (body, end)))
        self.label(body)
        self.loop_body(n.body, end, test)
        self.goto(test)
        self.label(end)

    def do_loop(self, n, negate: bool) -> None:
        body, test, end = self.new_label(), self.new_label(), self.new_label()
        self.label(body)
        self.loop_body(n.body, end, test)
        self.label(test)
        self.cond(n.condition, *((end, body) if negate else (body, end)))
        self.label(end)

    def visit_WhileStatement(self, n):
        self.while_loop(n, False)

    def visit_UntilStatement(self, n):
        self.while_loop(n, True)

    def visit_DoWhileStatement(self, n):
        self.do_loop(n, False)

    def visit_DoUntilStatement(self, n):
        self.do_loop(n, True)

    def visit_ForStatement(self, n):
        if n.init is not None:
            if n.init.kind == "Declaration":
                self.visit(n.init)
            else:
                self.effect(n.init)
        test, body, update, end = (self.new_label() for _ in range(4))
        self.label(test)
        if n.condition is not None:
            self.cond(n.condition, body, end)
        self.label(body)
        self.loop_body(n.body, end, update)       # continue runs the update part
        self.label(update)
        if n.update is not None:
            self.effect(n.update)
        self.goto(test)
        self.label(end)

    def visit_SwitchStatement(self, n):
        v = self.expr(n.expression)
        if isinstance(v, int) or v in self.fn.temps.types:
            pass
        else:                        # a variable: the body may change it
            t = self.new_temp(INT)
            self.emit("copy", v, None, t)
            v = t
        end = self.new_label()
        labels = [self.new_label() for _ in n.cases]
        default = end
        for case, lab in zip(n.cases, labels):
            if case.const_value is None:
                default = lab
            else:
                self.emit("if==", v, case.const_value, lab)
        self.goto(default)
        self.fn.jumps.append((end, None))
        for case, lab in zip(n.cases, labels):
            self.label(lab)
            for s in case.body:
                self.visit(s)
        self.fn.jumps.pop()
        self.label(end)

    def visit_JumpStatement(self, n):
        if n.keyword == "goto":
            self.goto(f"L_{self.fn.name}_{n.target}")
        elif n.keyword == "break":
            self.goto(self.fn.jumps[-1][0])
        else:                        # continue: nearest enclosing loop (skip switches)
            self.goto(next(c for _, c in reversed(self.fn.jumps) if c is not None))

    def visit_LabeledStatement(self, n):
        self.label(f"L_{self.fn.name}_{n.label}")
        self.stmt(n.statement)

    # ======================================================================
    # expressions
    # ======================================================================
    def visit_Literal(self, n):
        if n.literal_type == "string":
            return self.string_label(n.string_bytes)
        raise GenError(n, f"literal of type {n.literal_type} has no value")

    def visit_Identifier(self, n):
        sym = n.symbol
        return sym.ir_name            # for an array: its base address

    def visit_UnaryOp(self, n):
        op = n.operator
        if op in ("++", "--"):
            return self.incdec(n, True)
        a = self.expr(n.operand)
        t = n.operand.ctype
        if op == "+":
            return a
        if op == "-":
            return self.unary("negf", a, FLOAT) if t == FLOAT else self.unary("neg", a, INT)
        if op == "~":
            return self.unary("compl", a, INT)
        if op == "!":
            if t == FLOAT:
                return self.binary("==f", a, 0.0, INT)
            return self.unary("not", a, INT)
        raise GenError(n, f"unary operator '{op}' is not supported")

    def lvalue(self, target):
        """(read, write) for a scalar variable or an array element."""
        if target.kind == "Identifier":
            name = target.symbol.ir_name
            return (lambda: name), (lambda v: self.emit("copy", v, None, name))
        base, off, et = self.address(target)

        def read():
            t = self.new_temp(et)
            self.emit("load", base, off, t)
            return t
        return read, (lambda v: self.emit("store", v, off, base))

    def incdec(self, n, want_value: bool):
        """++ and --. The operand is a scalar variable or an array element."""
        target = n.operand
        read, write = self.lvalue(target)
        t = target.ctype
        place = read()
        old = None
        if n.position == "postfix" and want_value:
            old = place
            if target.kind == "Identifier":      # the variable changes, so keep a copy
                old = self.new_temp(t)
                self.emit("copy", place, None, old)
        if t == FLOAT:
            new = self.binary("+f" if n.operator == "++" else "-f", place, 1.0, FLOAT)
        else:
            new = self.binary("+" if n.operator == "++" else "-", place, 1, INT)
        new = self.convert(new, INT if t != FLOAT else FLOAT, t)
        write(new)
        if old is not None:
            return old
        return place if target.kind == "Identifier" else new

    def visit_BinaryOp(self, n):
        op = n.operator
        if op == ",":
            self.effect(n.left)
            return self.expr(n.right)
        if op in ("&&", "||"):
            return self.bool_value(n)
        lt, rt = n.left.ctype, n.right.ctype
        a = self.expr(n.left)
        b = self.expr(n.right)
        floaty = lt == FLOAT or rt == FLOAT
        if floaty and (op in ARITH_OPS or op in COMPARE_OPS):
            a = self.convert(a, lt, FLOAT)
            b = self.convert(b, rt, FLOAT)
            return self.binary(op + "f", a, b, INT if op in COMPARE_OPS else FLOAT)
        return self.binary(op, a, b, INT)

    def visit_Assignment(self, n):
        read, write = self.lvalue(n.target)
        tt = n.target.ctype
        vt = n.value.ctype
        if n.operator == "=":
            v = self.convert(self.expr(n.value), vt, tt)
            write(v)
            return v
        place = read()
        v = self.expr(n.value)
        op = COMPOUND_OPS[n.operator]
        if op in ARITH_OPS and (tt == FLOAT or vt == FLOAT):
            res = self.binary(op + "f", self.convert(place, tt, FLOAT), self.convert(v, vt, FLOAT), FLOAT)
            res_type = FLOAT
        else:
            res = self.binary(op, place, v, INT)
            res_type = INT
        res = self.convert(res, res_type, tt)
        write(res)
        return res if n.target.kind != "Identifier" else place

    def visit_CastExpression(self, n):
        v = self.expr(n.operand)
        return self.convert(v, n.operand.ctype, n.ctype)

    def bool_value(self, n):
        """&& or || used as a value: materialise 0 or 1."""
        t = self.new_temp(INT)
        yes, no, end = self.new_label(), self.new_label(), self.new_label()
        self.cond(n, yes, no)
        self.label(yes)
        self.emit("copy", 1, None, t)
        self.goto(end)
        self.label(no)
        self.emit("copy", 0, None, t)
        self.label(end)
        return t

    def visit_ConditionalExpression(self, n):
        t = self.new_temp(n.ctype)
        yes, no, end = self.new_label(), self.new_label(), self.new_label()
        self.cond(n.condition, yes, no)
        self.label(yes)
        self.emit("copy", self.convert(self.expr(n.then_value), n.then_value.ctype, n.ctype), None, t)
        self.goto(end)
        self.label(no)
        self.emit("copy", self.convert(self.expr(n.else_value), n.else_value.ctype, n.ctype), None, t)
        self.label(end)
        return t

    def address(self, n):
        """(base, byte offset, element type) of the element n = a[i]..[k]."""
        idxs = []
        while True:
            idxs.append(n.index)
            inner = n.array
            if inner.kind == "ArrayAccess" and isinstance(inner.ctype, ArrayType):
                n = inner
            else:
                break
        idxs.reverse()
        if isinstance(inner.ctype, ArrayType):
            base, dims, elem = inner.symbol.ir_name, inner.ctype.dims, inner.ctype.elem
        else:                        # a char* value: one index, char elements
            base, dims, elem = self.expr(inner), (None,), CHAR
            if inner.kind == "Literal":      # "abc"[i]: a data label is not a base name
                base = self.unary("copy", base, STRING)
        const, terms = 0, []
        for k, ix in enumerate(idxs):
            stride = elem.width * prod(dims[k + 1:])
            v = self.expr(ix)
            if isinstance(v, int):
                const += v * stride
            else:
                terms.append(v if stride == 1 else self.binary("*", v, stride, INT))
        off = None
        for t in terms:
            off = t if off is None else self.binary("+", off, t, INT)
        if off is None:
            off = const
        elif const:
            off = self.binary("+", off, const, INT)
        return base, off, elem if len(idxs) == len(dims) else n.ctype

    def visit_ArrayAccess(self, n):
        if isinstance(n.ctype, ArrayType):
            raise GenError(n, "unsupported feature: passing a row of a multi-dimensional "
                              "array (only whole arrays can be passed)")
        base, off, et = self.address(n)
        t = self.new_temp(et)
        self.emit("load", base, off, t)
        return t

    def visit_FunctionCall(self, n, discard: bool = False):
        if n.builtin == "printf":
            if not discard:
                raise GenError(n, "unsupported feature: using the value returned by printf")
            self.printf(n)
            return None
        if n.builtin == "scanf":
            return self.scanf(n, discard)
        if n.builtin == "atoi":
            self.emit("param", self.expr(n.args[0]))
            return self.call("atoi", 1, INT, discard)
        # user function: evaluate every argument first, then
        # push them left to right, then call. Recursion needs nothing special.
        sym = n.symbol
        args = [self.convert(self.expr(a), a.ctype, pt)
                for a, pt in zip(n.args, sym.type.params)]
        for v in args:
            self.emit("param", v)
        return self.call(sym.ir_name, len(args), sym.type.ret, discard)

    def call(self, name, count, ret, discard):
        """Emit the call; the result goes to a fresh temp unless unused or void."""
        if discard or ret == VOID:
            self.emit("call", name, count)
            return None
        t = self.new_temp(ret)
        self.emit("call", name, count, t)
        return t

    # --- scanf ------------------------------------------------------------
    READ_INTRINSIC = {"d": ("read_int", INT), "c": ("read_char", CHAR), "f": ("read_float", FLOAT)}

    def scanf(self, n, discard: bool):
        """One read_* call per conversion, as in C: after each read, scan_status says
        whether it worked. On failure scanf stops, leaving the variable unchanged.
        Its value is the number of conversions done, or -1 if the input ended
        before the first one (only computed when the value is used)."""
        end = self.new_label()
        count = None if discard else self.new_temp(INT)
        if count:
            self.emit("copy", 0, None, count)
        for (_, ch, target), skip in zip(n.format_items, n.scanf_skip):
            if ch == "s":
                self.emit("param", self.expr(target))
                self.emit("call", "read_str", 1)
                tmp = None
            else:
                name, t = self.READ_INTRINSIC[ch]
                _, write = self.lvalue(target)
                tmp = self.new_temp(t)
                if ch == "c" and skip:       # " %c": read again while the char is white space
                    again = self.new_label()
                    self.label(again)
                    self.emit("call", name, 0, tmp)
                    for w in (32, 9, 10, 13):
                        self.emit("if==", tmp, w, again)
                else:
                    self.emit("call", name, 0, tmp)
            status = self.new_temp(INT)
            self.emit("call", "scan_status", 0, status)
            ok = self.new_label()
            self.emit("if==", status, 0, ok)
            if count:                        # failed: -1 if nothing was read and the input ended
                self.emit("if!=", status, 2, end)
                self.emit("if!=", count, 0, end)
                self.emit("copy", -1, None, count)
            self.emit("goto", None, None, end)
            self.label(ok)
            if tmp:
                write(tmp)
            if count:
                self.emit("+", count, 1, count)
        self.label(end)
        return count

    # --- printf -----------------------------------------------------------
    def printf(self, n) -> None:
        """Lower printf to print_* calls. All arguments are evaluated first
        (as C does), then the pieces are printed from left to right."""
        pieces = []
        for item in n.format_items:
            if item[0] == "lit":
                pieces.append(("print_str", self.string_label(item[1])))
            else:
                _, ch, arg = item
                pieces.append((PRINT_INTRINSIC[ch], self.expr(arg)))
        for intrinsic, value in pieces:
            self.emit("param", value)
            self.emit("call", intrinsic, 1)


def generate(program, result) -> IRModule:
    """Generate IR for an analyzed Program."""
    return IRGenerator(result).generate(program)
