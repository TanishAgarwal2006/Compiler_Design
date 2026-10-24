"""
Semantic analysis: scopes, declarations and type checking.

`analyze(program)` walks the AST produced by Phase 2 once, in source order
(a name must be declared before use; prototypes are accepted), and
  * builds the scoped symbol table (symbol_table.py) with sizes and offsets,
  * checks types with the usual rules (structural equivalence, int ->
    float conversion, char promoted to int),
  * reports every error with its line number, without stopping at the first,
  * annotates the tree so the TAC generator never has to re-derive anything.

Annotations added to AST nodes (plain attributes)
    every expression   .ctype        its Type
                       .const_value  folded Python value, or None
    Identifier         .symbol       its Symbol
    FunctionCall       .scanf_skip   per scanf conversion: white space precedes it
    FunctionCall       .symbol       the function Symbol (None for builtins)
                       .builtin      'printf', 'scanf' or 'atoi' for builtins
                       .format_items parsed printf/scanf format (see below)
    InitDeclarator     .symbol       the variable Symbol
                       .init_kind    'none', 'scalar', 'array' or 'string'
                       .init_elems   array/string: [(flat_index, expr_or_int)]
    SwitchCase         .const_value  case value (None for default)
    FunctionDefinition .info         FunctionInfo (params, locals, frame size)

format_items for printf:  ('lit', bytes) | ('spec', char, arg_node)
format_items for scanf:   ('spec', char, target_node)   (target = operand of &,
                          or the char array for %s)

Out-of-scope features are accepted by the parser but reported here as
"unsupported feature: ...".
"""
from dataclasses import dataclass, field
from typing import Optional

from common import errors as _errors
from common.literals import char_value, string_bytes
from .symbol_table import Symbol, SymbolTable, FunctionInfo
from .type_system import (
    INT, CHAR, FLOAT, BOOL, VOID, STRING, ERROR, ArrayType, FunctionType, Type,
    is_error, is_arithmetic, is_integral, promote, common_arithmetic,
    is_string_like, assignable,
)

BUILTIN_FUNCS = {"printf", "scanf", "atoi"}
INTRINSIC_NAMES = {
    "print_int", "print_char", "print_str", "print_float",
    "read_int", "read_char", "read_str", "read_float", "scan_status",
}
RESERVED_NAMES = BUILTIN_FUNCS | INTRINSIC_NAMES

# Library functions of the full source language that this compiler does not
# provide; calling one is "unsupported", not a typo.
DYNAMIC_MEMORY_FUNCS = {"malloc", "calloc", "realloc", "free"}
FILE_IO_FUNCS = {"fopen", "fclose", "fread", "fwrite", "fprintf", "fscanf",
                 "fgets", "fputs", "fgetc", "fputc", "feof", "fseek", "ftell", "fflush"}
# Type names the lexer knows without a typedef (FILE, size_t, ...).
LIBRARY_TYPES = {"FILE", "size_t", "ptrdiff_t", "va_list"}

UNSUPPORTED_KINDS = {
    "LambdaExpression": "lambda functions",
    "ThisExpression": "'this'",
    "StructSpecifier": "struct and union",
    "UnionSpecifier": "struct and union",
    "MemberAccess": "member access ('.' and '->')",
    "ClassSpecifier": "classes",
    "BaseSpecifier": "classes",
    "AccessLabel": "classes",
    "NewExpression": "new",
    "DeleteExpression": "delete",
    "QualifiedName": "scope resolution ('::')",
    "VarArgsParameter": "variadic functions",
}

_COMPOUND_OPS = {
    "+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%",
    "&=": "&", "|=": "|", "^=": "^", "<<=": "<<", ">>=": ">>",
}
_ARITH_OPS = {"+", "-", "*", "/"}
_INTEGER_ONLY_OPS = {"%", "<<", ">>", "&", "|", "^"}
_COMPARE_OPS = {"<", "<=", ">", ">=", "==", "!="}
_LOGICAL_OPS = {"&&", "||"}


# ---------------------------------------------------------------------------
# constant folding helpers
# ---------------------------------------------------------------------------
def wrap32(v: int) -> int:
    return (int(v) + 2 ** 31) % 2 ** 32 - 2 ** 31


def wrap8(v: int) -> int:
    return (int(v) + 128) % 256 - 128


def _idiv(a: int, b: int) -> int:
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def convert_const(value, to_type: Type):
    """Convert a folded constant to the value it would have after assignment
    to something of to_type."""
    if to_type == FLOAT:
        return float(value)
    if to_type == CHAR:
        return wrap8(value)
    if to_type == BOOL:
        return 1 if value else 0
    if to_type == INT:
        return wrap32(value)
    return value


def fold_unary(op: str, v, result: Type):
    if op == "-":
        return -v if result == FLOAT else wrap32(-v)
    if op == "+":
        return v
    if op == "!":
        return 1 if v == 0 else 0
    if op == "~":
        return wrap32(~int(v))
    return None


def fold_binary(op: str, a, b, floaty: bool):
    if op in _LOGICAL_OPS:
        if op == "&&":
            return 1 if (a != 0 and b != 0) else 0
        return 1 if (a != 0 or b != 0) else 0
    if op in _COMPARE_OPS:
        return int({"<": a < b, "<=": a <= b, ">": a > b,
                    ">=": a >= b, "==": a == b, "!=": a != b}[op])
    if op in "+-*" and len(op) == 1:
        r = {"+": a + b, "-": a - b, "*": a * b}[op]
        return float(r) if floaty else wrap32(r)
    if op == "/":
        if b == 0:
            return None
        return a / b if floaty else wrap32(_idiv(int(a), int(b)))
    if op == "%":
        if b == 0:
            return None
        return wrap32(int(a) - int(b) * _idiv(int(a), int(b)))
    if op in ("<<", ">>"):
        if not 0 <= b < 32:
            return None
        return wrap32(int(a) << int(b)) if op == "<<" else int(a) >> int(b)
    if op in ("&", "|", "^"):
        a, b = int(a), int(b)
        return wrap32({"&": a & b, "|": a | b, "^": a ^ b}[op])
    return None


# ---------------------------------------------------------------------------
# printf / scanf format parsing
# ---------------------------------------------------------------------------
def parse_format(fmt: bytes) -> list:
    """Split a format string into ('lit', bytes) and ('spec', char) items.
    Supported conversions: %d %i %c %f %s and %%. Raises ValueError with a
    message for anything else (width, precision, length modifiers, ...)."""
    items = []
    lit = bytearray()
    i = 0
    while i < len(fmt):
        ch = fmt[i]
        if ch != ord("%"):
            lit.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(fmt):
            raise ValueError("format string ends with a lone '%'")
        c = chr(fmt[i])
        if c == "%":
            lit.append(ord("%"))
            i += 1
        elif c in "dicfs":
            if lit:
                items.append(("lit", bytes(lit)))
                lit = bytearray()
            items.append(("spec", "d" if c == "i" else c))
            i += 1
        else:
            j = i
            while j < len(fmt) and not chr(fmt[j]).isalpha():
                j += 1
            spec = fmt[i:j + 1].decode("latin-1")
            raise ValueError(f"unsupported format specifier '%{spec}' "
                             f"(supported: %d %i %c %f %s %%)")
    if lit:
        items.append(("lit", bytes(lit)))
    return items


# ---------------------------------------------------------------------------
@dataclass
class SemanticResult:
    table: SymbolTable
    functions: dict
    globals: list
    typedefs: list = field(default_factory=list)
    enums: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class SemanticAnalyzer:
    def __init__(self):
        self.table = SymbolTable()
        self._errors = []            # (line, sequence, text)
        self._seq = 0
        self.fn_ret: Type = VOID
        self.fn_name: Optional[str] = None
        self.ctx_stack = []          # 'loop' / 'switch' for break and continue
        self.labels = set()
        self.gotos = []
        self.typedefs = []
        self.enums = []
        self.extern_pending = []      # "extern" globals still waiting for their definition

    # --- error reporting --------------------------------------------------
    def err(self, node, message: str) -> None:
        line = node if isinstance(node, int) else (getattr(node, "line", 0) or 0)
        self._seq += 1
        self._errors.append((line, self._seq, f"semantic error at line {line}: {message}"))

    def unsupported(self, node, what: str) -> None:
        self.err(node, f"unsupported feature: {what}")

    @property
    def in_fn(self) -> bool:
        return self.table._fn is not None

    # --- entry point ------------------------------------------------------
    def run(self, program) -> SemanticResult:
        for decl in program.declarations:
            if decl.kind == "FunctionDefinition":
                self.function_definition(decl)
            elif decl.kind == "Declaration":
                self.declaration(decl)
            else:
                self.unsupported(decl, decl.kind)
        self.check_main()
        for sym in self.extern_pending:
            self.err(sym.line, f"extern variable '{sym.name}' is declared but never defined")
        ordered = [text for _, _, text in sorted(self._errors)]
        _errors.semantic_errors.extend(ordered)
        return SemanticResult(self.table, self.table.functions, self.table.globals,
                              self.typedefs, self.enums, ordered)

    def check_main(self) -> None:
        main = self.table.lookup_global("main")
        if main is None or main.kind != "func" or not main.defined:
            self.err(1, "no 'main' function defined")

    # ======================================================================
    # types and declarations
    # ======================================================================
    def base_type(self, ts):
        """Resolve a type specifier to (Type, is_const)."""
        if ts is None:
            return ERROR, False
        if ts.kind == "EnumSpecifier":
            if ts.enumerators is None and ts.tag not in self.table.enum_tags:
                self.err(ts, f"unknown enum '{ts.tag}'")
                return ERROR, False
            return INT, False
        if ts.kind != "TypeSpecifier":
            self.unsupported(ts, UNSUPPORTED_KINDS.get(ts.kind, ts.kind))
            return ERROR, False
        words = ts.name.split()
        is_const = "const" in words
        words = [w for w in words if w not in ("const", "volatile")]
        if "auto" in words:
            self.unsupported(ts, "'auto' type deduction (write the type out)")
            return ERROR, False
        if len(words) == 1:
            sym = self.table.lookup(words[0])
            if sym is not None and sym.kind == "typedef":
                return sym.type, is_const
            if words[0] in LIBRARY_TYPES:
                self.unsupported(ts, f"library type '{words[0]}'")
                return ERROR, False
        if "void" in words:
            return VOID, is_const
        if "bool" in words or "_Bool" in words:
            return BOOL, is_const
        if "float" in words or "double" in words:
            return FLOAT, is_const
        if "char" in words:
            return CHAR, is_const
        return INT, is_const

    def declare_enumerators(self, es) -> None:
        if es.tag:
            self.table.enum_tags.add(es.tag)
        nxt = 0
        for en in es.enumerators:
            if en.value is not None:
                v = self.const_expr(en.value, "enumerator value")
                if v is not None:
                    nxt = int(v)
            sym = Symbol(en.name, "enum_const", INT, line=en.line or es.line or 0,
                         ir_name=en.name, const_value=nxt, is_const=True)
            if self.table.declare(sym):
                self.err(en, f"redeclaration of '{en.name}'")
            else:
                self.enums.append((en.name, nxt))
            nxt += 1

    def build_type(self, base: Type, d, ctx: str) -> Type:
        """Combine a base type with a declarator's pointers and dimensions.
        ctx is 'var', 'param' or 'return'."""
        if is_error(base):
            return ERROR
        if d.is_reference:
            self.unsupported(d, f"references ('&' in the declaration of '{d.name}')")
            return ERROR
        pl = d.pointer_level
        dims = []
        for k, dim in enumerate(d.dimensions):
            if dim.size is None:
                if k != 0:
                    self.err(d, f"array size missing for dimension {k + 1} of '{d.name}'")
                    return ERROR
                dims.append(None)
            else:
                v = self.const_expr(dim.size, f"array size of '{d.name}'")
                if v is None:
                    return ERROR
                if not isinstance(v, int) or v <= 0:
                    self.err(d, f"array size of '{d.name}' must be a positive integer")
                    return ERROR
                dims.append(v)
        if pl:
            if base == CHAR and not dims and pl == 1:
                return STRING
            if base == CHAR and ctx == "param" and (
                    (pl == 2 and not dims) or (pl == 1 and len(dims) == 1)):
                return ArrayType(STRING, (dims[0] if dims else None,))
            self.unsupported(d, "pointers (only 'char *' strings and 'argv' are accepted)")
            return ERROR
        if base == VOID:
            if dims:
                self.err(d, f"array '{d.name}' of void")
                return ERROR
            return VOID
        if isinstance(base, ArrayType):
            if not dims:
                return base
            return ArrayType(base.elem, tuple(dims) + base.dims)
        if dims:
            return ArrayType(base, tuple(dims))
        return base

    # --- declarations -----------------------------------------------------
    def declaration(self, decl) -> None:
        ts = decl.type_spec
        if ts is not None and ts.kind == "EnumSpecifier" and ts.enumerators:
            self.declare_enumerators(ts)
        base, is_const = self.base_type(ts)
        if decl.storage == "typedef":
            for idecl in decl.declarators:
                d = idecl.declarator
                t = self.build_type(base, d, "var")
                sym = Symbol(d.name, "typedef", t, line=d.line or decl.line or 0)
                if self.table.declare(sym):
                    self.err(d, f"redeclaration of '{d.name}'")
                else:
                    self.typedefs.append((d.name, t))
            return
        if decl.storage == "static" and self.in_fn:
            self.unsupported(decl, "static local variables")
        for idecl in decl.declarators:
            if idecl.declarator.scope:
                self.unsupported(idecl.declarator, "member functions ('Class::name')")
            elif idecl.declarator.kind_name == "function":
                self.prototype(base, idecl.declarator, decl)
            else:
                self.variable(base, is_const, idecl, decl)

    def variable(self, base: Type, is_const: bool, idecl, decl) -> None:
        d = idecl.declarator
        t = self.build_type(base, d, "var")
        if t == VOID:
            self.err(d, f"variable '{d.name}' declared void")
            t = ERROR
        # "extern int x;" only announces a global; "int x = 1;" later defines it.
        is_extern = (decl.storage == "extern" and not self.in_fn and idecl.initializer is None)
        if not self.in_fn and not is_error(t):
            prev = self.table.lookup_global(d.name)
            if prev is not None and prev.kind == "var" and prev.type == t and not prev.defined:
                idecl.symbol = prev
                idecl.init_kind = "none"
                if not is_extern:                      # this declaration is the definition
                    prev.defined = True
                    prev.is_const = is_const and t != STRING
                    self.extern_pending.remove(prev)
                    self.initializer(prev, idecl)
                    self.table.allocate(prev)
                return
            if prev is not None and prev.kind == "var" and prev.type == t and is_extern:
                idecl.symbol = prev                    # extern after the definition: nothing to do
                idecl.init_kind = "none"
                return
        sym = Symbol(d.name, "var", t, line=d.line or decl.line or 0,
                     is_const=is_const and t != STRING, storage=decl.storage, defined=not is_extern)
        idecl.symbol = sym
        idecl.init_kind = "none"
        existing = self.table.declare(sym)
        if existing is not None:
            self.err(d, f"redeclaration of '{d.name}' (previous declaration at line {existing.line})")
            return
        if is_extern:
            self.extern_pending.append(sym)
            return
        self.initializer(sym, idecl)
        if isinstance(sym.type, ArrayType) and not sym.type.is_complete and sym.kind == "var":
            self.err(d, f"array size missing in declaration of '{d.name}'")
            sym.type = ERROR
        self.table.allocate(sym)

    # --- initializers -----------------------------------------------------
    def initializer(self, sym: Symbol, idecl) -> None:
        init = idecl.initializer
        if init is None:
            return
        t = sym.type
        is_global = not self.in_fn
        if is_error(t):
            if init.kind != "InitializerList":
                self.expr(init)
            return
        if isinstance(t, ArrayType):
            self.array_initializer(sym, idecl, init, is_global)
            return
        if init.kind == "InitializerList":
            self.err(init, f"braces around scalar initializer of '{sym.name}'")
            return
        vt = self.expr(init)
        idecl.init_kind = "scalar"
        if not assignable(t, vt):
            self.err(init, f"cannot initialize '{sym.name}' of type {t} with a value of type {vt}")
            return
        if is_global:
            if t == STRING:
                if init.kind != "Literal" or init.literal_type != "string":
                    self.err(init, f"initializer of global '{sym.name}' must be a string literal")
            elif init.const_value is None:
                self.err(init, f"initializer of global '{sym.name}' is not a constant expression")
        if t != STRING and init.const_value is not None and not is_error(vt):
            idecl.init_value = convert_const(init.const_value, t)
            if sym.is_const:
                sym.const_value = idecl.init_value

    def array_initializer(self, sym: Symbol, idecl, init, is_global: bool) -> None:
        t: ArrayType = sym.type
        name = sym.name
        # char s[] = "text";
        if init.kind == "Literal" and init.literal_type == "string":
            self.expr(init)
            if t.elem != CHAR or len(t.dims) != 1:
                self.err(init, f"cannot initialize array '{name}' of type {t} with a string")
                return
            data = init.string_bytes
            if t.dims[0] is None:
                sym.type = t = ArrayType(CHAR, (len(data) + 1,))
            elif len(data) > t.dims[0]:
                self.err(init, f"string initializer is too long for '{name}'")
                return
            elems = [(i, b) for i, b in enumerate(data)]
            if len(data) < t.dims[0]:
                elems.append((len(data), 0))
            idecl.init_kind = "string"
            idecl.init_elems = elems
            return
        if init.kind != "InitializerList":
            self.expr(init)
            self.err(init, f"array '{name}' needs a brace-enclosed initializer")
            return
        dims = t.dims
        row = 1
        for d in dims[1:]:
            row *= d
        values = init.values
        nested = [v.kind == "InitializerList" for v in values]
        if any(nested) and not all(nested):
            self.err(init, f"mixed nested and flat initializers for '{name}' are not supported")
            return
        if len(dims) == 1 and any(nested):
            self.err(init, f"too many braces in initializer of '{name}'")
            return
        elems = []
        if len(dims) > 1 and all(nested) and values:
            count = len(values)
            if dims[0] is not None and count > dims[0]:
                self.err(init, f"too many initializers for '{name}'")
                return
            if not self.flatten_nested(values, dims, 0, elems, name, init):
                return
            if dims[0] is None:
                sym.type = t = ArrayType(t.elem, (count,) + dims[1:])
        else:
            count = len(values)
            capacity = None if dims[0] is None else dims[0] * row
            if capacity is not None and count > capacity:
                self.err(init, f"too many initializers for '{name}'")
                return
            for i, v in enumerate(values):
                elems.append((i, v))
            if dims[0] is None:
                sym.type = t = ArrayType(t.elem, (max(1, -(-count // row)),) + dims[1:])
        for _, e in elems:
            et = self.expr(e)
            if not assignable(t.elem, et):
                self.err(e, f"cannot initialize element of '{name}' ({t.elem}) with a value of type {et}")
            elif is_global and e.const_value is None:
                self.err(e, f"initializer element of global '{name}' is not constant")
        idecl.init_kind = "array"
        idecl.init_elems = elems

    def flatten_nested(self, lst, dims, base, elems, name, node) -> bool:
        """Flatten a fully nested initializer into (flat_index, expr) pairs."""
        if dims[0] is not None and len(lst) > dims[0]:
            self.err(node, f"too many initializers for '{name}'")
            return False
        row = 1
        for d in dims[1:]:
            row *= d
        for i, v in enumerate(lst):
            if len(dims) == 1:
                if v.kind == "InitializerList":
                    self.err(v, f"too many braces in initializer of '{name}'")
                    return False
                elems.append((base + i, v))
            else:
                if v.kind != "InitializerList":
                    self.err(v, f"mixed nested and flat initializers for '{name}' are not supported")
                    return False
                if not self.flatten_nested(v.values, dims[1:], base + i * row, elems, name, v):
                    return False
        return True

    # --- functions --------------------------------------------------------
    def param_types(self, params, d):
        """Return a tuple of parameter types, or None after an error."""
        if not params:
            return ()
        if len(params) == 1 and params[0].kind == "Parameter" and \
                params[0].declarator is None and params[0].type_spec.name.split()[-1] == "void":
            return ()
        types = []
        ok = True
        for p in params:
            if p.kind == "VarArgsParameter":
                self.unsupported(p, "variadic functions")
                ok = False
                continue
            base, _ = self.base_type(p.type_spec)
            if p.declarator is None:
                t = base
            else:
                t = self.build_type(base, p.declarator, "param")
            if t == VOID:
                self.err(p, "parameter cannot have type void")
                t = ERROR
            types.append(t)
        return tuple(types) if ok else None

    def function_type(self, ret_base: Type, d) -> Optional[FunctionType]:
        if d.dimensions:
            self.err(d, f"function '{d.name}' cannot return an array")
            return None
        ret = self.build_type(ret_base, type(d)(d.name, "variable", [], None, d.pointer_level, d.is_reference, d.line), "var") \
            if (d.pointer_level or d.is_reference) else ret_base
        if isinstance(ret, ArrayType):
            self.err(d, f"function '{d.name}' cannot return an array")
            return None
        ptypes = self.param_types(d.params, d)
        if ptypes is None:
            return None
        return FunctionType(ret, ptypes)

    def declare_function(self, name, ftype, node, defined: bool, storage=None) -> Optional[Symbol]:
        if name in BUILTIN_FUNCS:
            self.err(node, f"'{name}' is a reserved name and cannot be redefined")
            return None
        existing = self.table.lookup_global(name)
        if existing is not None:
            if existing.kind != "func":
                self.err(node, f"'{name}' redeclared as a different kind of symbol")
                return None
            if existing.type != ftype:
                self.err(node, f"conflicting types for '{name}' (previous: {existing.type})")
                return None
            if defined and existing.defined:
                self.err(node, f"redefinition of function '{name}'")
                return None
            if defined:
                existing.defined = True
                existing.line = node.line or existing.line
            return existing
        # a user function named like an IR intrinsic (print_int...) gets a distinct IR name
        sym = Symbol(name, "func", ftype, line=node.line or 0,
                     ir_name=name + ".u" if name in INTRINSIC_NAMES else name,
                     defined=defined, storage=storage)
        saved = self.table.current
        self.table.current = self.table.global_scope
        self.table.declare(sym)
        self.table.current = saved
        return sym

    def prototype(self, base: Type, d, decl) -> None:
        ftype = self.function_type(base, d)
        if ftype is None:
            return
        self.declare_function(d.name, ftype, d, defined=False, storage=decl.storage)

    def function_definition(self, fd) -> None:
        d = fd.declarator
        if d.scope or d.kind_name in ("constructor", "destructor"):
            self.unsupported(fd, "member functions, constructors and destructors")
            return
        base, _ = self.base_type(fd.return_type)
        ftype = self.function_type(base, d)
        if ftype is None:
            return
        sym = self.declare_function(d.name, ftype, d, defined=True, storage=fd.storage)
        if sym is None:
            return
        if d.name == "main":
            self.check_main_signature(d, ftype)
        info = self.table.begin_function(sym)
        self.table.push("function")
        saved = (self.fn_ret, self.fn_name, self.ctx_stack, self.labels, self.gotos)
        self.fn_ret, self.fn_name = ftype.ret, d.name
        self.ctx_stack, self.labels, self.gotos = [], set(), []
        # parameters
        plist = [] if (not d.params or not ftype.params) else d.params
        for p, pt in zip(plist, ftype.params):
            pd = p.declarator
            if pd is None or not pd.name:
                self.err(p, f"parameter name omitted in definition of '{d.name}'")
                continue
            psym = Symbol(pd.name, "param", pt, line=pd.line or p.line or 0)
            if self.table.declare(psym):
                self.err(pd, f"duplicate parameter '{pd.name}'")
                continue
            self.table.allocate(psym)
        self.table.mark_body_started()
        self.collect_labels(fd.body)
        for item in fd.body.items:
            self.stmt(item)
        for g in self.gotos:
            if g.target not in self.labels:
                self.err(g, f"goto to undefined label '{g.target}'")
        self.table.pop()
        self.table.end_function()
        fd.info = info
        self.fn_ret, self.fn_name, self.ctx_stack, self.labels, self.gotos = saved

    def check_main_signature(self, d, ftype) -> None:
        ok_ret = ftype.ret in (INT, VOID)
        ps = ftype.params
        ok_params = ps == () or (len(ps) == 2 and ps[0] == INT and ps[1] == ArrayType(STRING, (None,)))
        if not (ok_ret and ok_params):
            self.err(d, "unsupported signature for 'main' "
                        "(use main(), main(void) or main(int argc, char *argv[]))")

    def collect_labels(self, node) -> None:
        """Pre-scan a function body so forward gotos can be checked."""
        if isinstance(node, list):
            for x in node:
                self.collect_labels(x)
            return
        if not hasattr(node, "kind"):
            return
        if node.kind == "LabeledStatement":
            if node.label in self.labels:
                self.err(node, f"duplicate label '{node.label}'")
            self.labels.add(node.label)
        for v in vars(node).values():
            if isinstance(v, list) or hasattr(v, "kind"):
                self.collect_labels(v)

    # ======================================================================
    # statements
    # ======================================================================
    def stmt(self, n) -> None:
        if n is None:
            return
        handler = getattr(self, "stmt_" + n.kind, None)
        if handler is None:
            self.unsupported(n, UNSUPPORTED_KINDS.get(n.kind, n.kind))
            return
        handler(n)

    def stmt_Declaration(self, n):
        self.declaration(n)

    def stmt_CompoundStatement(self, n):
        self.table.push("block")
        for item in n.items:
            self.stmt(item)
        self.table.pop()

    def stmt_ExpressionStatement(self, n):
        if n.expression is not None:
            self.expr(n.expression)

    def cond(self, e, what: str) -> None:
        t = self.expr(e)
        if not is_arithmetic(t) and not is_error(t):
            self.err(e, f"{what} must be an int, char or float value (got {t})")

    def stmt_IfStatement(self, n):
        self.cond(n.condition, "condition of 'if'")
        self.stmt(n.then_branch)
        self.stmt(n.else_branch)

    def loop_body(self, body):
        self.ctx_stack.append("loop")
        self.stmt(body)
        self.ctx_stack.pop()

    def stmt_WhileStatement(self, n):
        self.cond(n.condition, "condition of 'while'")
        self.loop_body(n.body)

    def stmt_UntilStatement(self, n):
        self.cond(n.condition, "condition of 'until'")
        self.loop_body(n.body)

    def stmt_DoWhileStatement(self, n):
        self.loop_body(n.body)
        self.cond(n.condition, "condition of 'do-while'")

    def stmt_DoUntilStatement(self, n):
        self.loop_body(n.body)
        self.cond(n.condition, "condition of 'do-until'")

    def stmt_ForStatement(self, n):
        self.table.push("block")
        if n.init is not None:
            if n.init.kind == "Declaration":
                self.declaration(n.init)
            else:
                self.expr(n.init)
        if n.condition is not None:
            self.cond(n.condition, "condition of 'for'")
        if n.update is not None:
            self.expr(n.update)
        self.loop_body(n.body)
        self.table.pop()

    def stmt_SwitchStatement(self, n):
        t = self.expr(n.expression)
        if not is_integral(t) and not is_error(t):
            self.err(n.expression, f"switch expression must be an int or char (got {t})")
        self.table.push("block")
        self.ctx_stack.append("switch")
        seen = set()
        has_default = False
        for case in n.cases:
            case.const_value = None
            if case.value is None:
                if has_default:
                    self.err(case, "duplicate 'default' label in switch")
                has_default = True
            else:
                v = self.const_expr(case.value, "case value")
                if v is not None:
                    if not isinstance(v, int):
                        self.err(case, "case value must be an integer constant")
                    else:
                        case.const_value = v
                        if v in seen:
                            self.err(case, f"duplicate case value {v}")
                        seen.add(v)
            for s in case.body:
                self.stmt(s)
        self.ctx_stack.pop()
        self.table.pop()

    def stmt_ReturnStatement(self, n):
        ret = self.fn_ret
        if n.value is None:
            if ret not in (VOID, ERROR):
                self.err(n, f"non-void function '{self.fn_name}' should return a value")
            return
        vt = self.expr(n.value)
        if ret == VOID:
            self.err(n, f"void function '{self.fn_name}' should not return a value")
        elif not assignable(ret, vt):
            self.err(n, f"cannot return a value of type {vt} from function '{self.fn_name}' returning {ret}")

    def stmt_JumpStatement(self, n):
        kw = n.keyword
        if kw == "break":
            if not self.ctx_stack:
                self.err(n, "'break' outside a loop or switch")
        elif kw == "continue":
            if "loop" not in self.ctx_stack:
                self.err(n, "'continue' outside a loop")
        elif kw == "goto":
            self.gotos.append(n)

    def stmt_LabeledStatement(self, n):
        self.stmt(n.statement)

    # ======================================================================
    # expressions
    # ======================================================================
    def expr(self, n) -> Type:
        n.const_value = None
        handler = getattr(self, "expr_" + n.kind, None)
        if handler is None:
            self.unsupported(n, UNSUPPORTED_KINDS.get(n.kind, n.kind))
            t = ERROR
        else:
            t = handler(n)
        n.ctype = t
        return t

    def const_expr(self, n, what: str):
        """Evaluate n as a compile-time constant; report and return None if it is not one."""
        self.expr(n)
        if n.const_value is None:
            if not is_error(n.ctype):
                self.err(n, f"{what} must be a constant expression")
            return None
        return n.const_value

    def expr_Literal(self, n):
        lt = n.literal_type
        if lt == "int":
            n.const_value = wrap32(n.value)
            return INT
        if lt == "float":
            n.const_value = float(n.value)
            return FLOAT
        if lt == "bool":
            n.const_value = 1 if str(n.value) == "true" else 0
            return INT
        try:
            if lt == "char":
                n.const_value = char_value(n.value)
                return CHAR
            if lt == "string":
                n.string_bytes = string_bytes(n.value)
                return STRING
        except ValueError as exc:
            self.err(n, str(exc))
            return ERROR
        self.err(n, f"unknown literal type '{lt}'")
        return ERROR

    def expr_Identifier(self, n):
        sym = self.table.lookup(n.name)
        if sym is None:
            self.err(n, f"use of undeclared identifier '{n.name}'")
            return ERROR
        n.symbol = sym
        if sym.kind == "func":
            self.err(n, f"function '{n.name}' used as a value (call it with parentheses)")
            return ERROR
        if sym.kind == "typedef":
            self.err(n, f"type name '{n.name}' used as a value")
            return ERROR
        if sym.const_value is not None and not isinstance(sym.type, ArrayType):
            n.const_value = sym.const_value
        return sym.type

    def need_arith(self, node, t: Type, what: str) -> bool:
        if is_arithmetic(t) or is_error(t):
            return True
        if t == VOID:
            self.err(node, f"void value used in {what}")
        else:
            self.err(node, f"{what} needs an int, char or float operand (got {t})")
        return False

    def expr_BinaryOp(self, n):
        op = n.operator
        lt = self.expr(n.left)
        rt = self.expr(n.right)
        if op == ",":
            n.const_value = None
            return rt
        what = f"operator '{op}'"
        ok = self.need_arith(n.left, lt, what) and self.need_arith(n.right, rt, what)
        if not ok or is_error(lt) or is_error(rt):
            return ERROR if not ok else (INT if op in _COMPARE_OPS | _LOGICAL_OPS else ERROR)
        if op in _INTEGER_ONLY_OPS and (not is_integral(lt) or not is_integral(rt)):
            self.err(n, f"operator '{op}' needs int or char operands (got {lt} and {rt})")
            return ERROR
        if op in ("/", "%") and n.right.const_value == 0:
            self.err(n, "division by zero")
            return INT if op == "%" else common_arithmetic(lt, rt)
        if op in _ARITH_OPS:
            result = common_arithmetic(lt, rt)
        else:
            result = INT
        a, b = n.left.const_value, n.right.const_value
        if a is not None and b is not None:
            floaty = lt == FLOAT or rt == FLOAT
            n.const_value = fold_binary(op, a, b, floaty if op in _ARITH_OPS else False)
        return result

    def lvalue_root(self, n):
        while n is not None and n.kind == "ArrayAccess":
            n = n.array
        return getattr(n, "symbol", None) if n is not None and n.kind == "Identifier" else None

    def check_lvalue(self, n, t: Type, what: str) -> bool:
        if is_error(t):
            return False
        ok = False
        if n.kind == "Identifier":
            sym = getattr(n, "symbol", None)
            ok = sym is not None and sym.kind in ("var", "param") and \
                (is_arithmetic(t) or t == STRING)
        elif n.kind == "ArrayAccess":
            ok = is_arithmetic(t)
        if not ok:
            if isinstance(t, ArrayType):
                self.err(n, f"cannot {what} an array")
            else:
                self.err(n, f"cannot {what} this expression (it is not a modifiable variable)")
            return False
        root = self.lvalue_root(n)
        if root is not None and root.is_const:
            self.err(n, f"cannot {what} read-only variable '{root.name}'")
            return False
        return True

    def expr_Assignment(self, n):
        tt = self.expr(n.target)
        vt = self.expr(n.value)
        op = n.operator
        good = self.check_lvalue(n.target, tt, "assign to")
        if op == "=":
            if good and not is_error(vt) and not assignable(tt, vt):
                self.err(n, f"cannot assign a value of type {vt} to {tt}")
            return tt if not is_error(tt) else ERROR
        bop = _COMPOUND_OPS.get(op)
        if bop is None:
            self.err(n, f"unknown assignment operator '{op}'")
            return tt
        if good and not is_arithmetic(tt):
            self.err(n, f"operator '{op}' needs an int, char or float variable (got {tt})")
        elif good and self.need_arith(n.value, vt, f"operator '{op}'"):
            if bop in _INTEGER_ONLY_OPS and (not is_integral(tt) or not is_integral(vt)):
                self.err(n, f"operator '{op}' needs int or char operands (got {tt} and {vt})")
            elif bop in ("/", "%") and n.value.const_value == 0:
                self.err(n, "division by zero")
        return tt

    def expr_UnaryOp(self, n):
        op = n.operator
        if op == "sizeof":
            return self.sizeof(n)
        if op == "&":
            self.expr(n.operand)
            self.err(n, "address-of '&' is only supported inside scanf arguments")
            return ERROR
        if op == "*":
            self.expr(n.operand)
            self.unsupported(n, "pointer dereference '*'")
            return ERROR
        t = self.expr(n.operand)
        if op in ("++", "--"):
            if self.check_lvalue(n.operand, t, f"apply '{op}' to") and t == STRING:
                self.err(n, f"cannot apply '{op}' to {t}")
            return t if is_arithmetic(t) else ERROR
        if not self.need_arith(n.operand, t, f"operator '{op}'") or is_error(t):
            return ERROR
        if op == "~" and not is_integral(t):
            self.err(n, f"operator '~' needs an int or char operand (got {t})")
            return ERROR
        result = INT if op in ("!", "~") else promote(t)
        v = n.operand.const_value
        if v is not None:
            n.const_value = fold_unary(op, v, result)
        return result

    def sizeof(self, n):
        operand = n.operand
        if operand.kind == "TypeSpecifier" or operand.kind in ("EnumSpecifier", "StructSpecifier"):
            t, _ = self.base_type(operand)
        else:
            t = self.expr(operand)
        if is_error(t):
            return INT
        if t == VOID:
            self.err(n, "sizeof applied to void")
            return INT
        n.const_value = t.width
        return INT

    def expr_ConditionalExpression(self, n):
        self.cond(n.condition, "condition of '?:'")
        a = self.expr(n.then_value)
        b = self.expr(n.else_value)
        if is_error(a) or is_error(b):
            return ERROR
        if is_arithmetic(a) and is_arithmetic(b):
            result = common_arithmetic(a, b) if (a == FLOAT or b == FLOAT) else (
                CHAR if a == CHAR and b == CHAR else INT)
            c, x, y = n.condition.const_value, n.then_value.const_value, n.else_value.const_value
            if c is not None and x is not None and y is not None:
                n.const_value = convert_const(x if c != 0 else y, result)
            return result
        if is_string_like(a) and is_string_like(b):
            return STRING
        self.err(n, f"branches of '?:' have incompatible types {a} and {b}")
        return ERROR

    def expr_CastExpression(self, n):
        vt = self.expr(n.operand)
        base, _ = self.base_type(n.type_spec)
        if is_error(base):
            return ERROR
        if n.pointer_level:
            self.unsupported(n, "casts to pointer types")
            return ERROR
        if not is_arithmetic(base):
            self.err(n, f"cannot cast to type {base}")
            return ERROR
        if not self.need_arith(n.operand, vt, "a cast") or is_error(vt):
            return base
        v = n.operand.const_value
        if v is not None:
            n.const_value = convert_const(int(v) if base != FLOAT else v, base)
        return base

    def expr_ArrayAccess(self, n):
        bt = self.expr(n.array)
        it = self.expr(n.index)
        if not is_integral(it) and not is_error(it):
            self.err(n.index, f"array index must be an int or char (got {it})")
        if isinstance(bt, ArrayType):
            return bt.row_type()
        if bt == STRING:
            return CHAR
        if not is_error(bt):
            self.err(n, f"subscripted value is not an array (type {bt})")
        return ERROR

    # --- calls ------------------------------------------------------------
    def arg_ok(self, p: Type, a: Type) -> bool:
        if is_error(p) or is_error(a):
            return True
        if is_arithmetic(p):
            return is_arithmetic(a)
        if p == STRING:
            return is_string_like(a)
        if isinstance(p, ArrayType):
            if a == STRING:          # char s[] and char *s are the same thing in C
                return p.elem == CHAR and len(p.dims) == 1
            return (isinstance(a, ArrayType) and p.elem == a.elem
                    and len(p.dims) == len(a.dims) and p.dims[1:] == a.dims[1:])
        return False

    def expr_FunctionCall(self, n):
        callee = n.callee
        n.symbol = None
        n.builtin = None
        if callee.kind == "MemberAccess":
            self.unsupported(n, "member function calls ('.' and '->')")
            for a in n.args:
                self.expr(a)
            return ERROR
        if callee.kind != "Identifier":
            self.err(n, "only direct calls by function name are supported")
            for a in n.args:
                self.expr(a)
            return ERROR
        name = callee.name
        sym = self.table.lookup(name)
        if sym is None and name in BUILTIN_FUNCS:
            n.builtin = name
            callee.ctype = FunctionType(INT, ())
            return {"printf": self.call_printf, "scanf": self.call_scanf,
                    "atoi": self.call_atoi}[name](n)
        if sym is None and name in DYNAMIC_MEMORY_FUNCS:
            self.unsupported(n, f"dynamic memory ('{name}')")
            for a in n.args:
                self.expr(a)
            return ERROR
        if sym is None and name in FILE_IO_FUNCS:
            self.unsupported(n, f"file I/O ('{name}')")
            for a in n.args:
                self.expr(a)
            return ERROR
        if sym is None:
            self.err(n, f"call to undeclared function '{name}'")
            for a in n.args:
                self.expr(a)
            return ERROR
        if sym.kind != "func":
            self.err(n, f"'{name}' is not a function")
            for a in n.args:
                self.expr(a)
            return ERROR
        n.symbol = callee.symbol = sym
        callee.ctype = sym.type
        arg_types = [self.expr(a) for a in n.args]
        params = sym.type.params
        if len(arg_types) != len(params):
            self.err(n, f"function '{name}' expects {len(params)} argument(s) but {len(arg_types)} were given")
        else:
            for k, (pt, at) in enumerate(zip(params, arg_types), start=1):
                if not self.arg_ok(pt, at):
                    self.err(n.args[k - 1], f"argument {k} of '{name}': cannot pass {at} where {pt} is expected")
        return sym.type.ret

    def literal_format(self, n, fname: str):
        """Return the parsed format items of the first argument, or None."""
        if not n.args:
            self.err(n, f"{fname} needs a format string")
            return None
        fmt = n.args[0]
        self.expr(fmt)
        if fmt.kind != "Literal" or fmt.literal_type != "string":
            self.err(fmt, f"the format of {fname} must be a string literal")
            return None
        try:
            return parse_format(fmt.string_bytes)
        except ValueError as exc:
            self.err(fmt, f"{fname}: {exc}")
            return None

    def call_printf(self, n):
        items = self.literal_format(n, "printf")
        args = n.args[1:]
        arg_types = [self.expr(a) for a in args]
        if items is None:
            return INT
        specs = [it for it in items if it[0] == "spec"]
        if len(specs) != len(args):
            self.err(n, f"printf format has {len(specs)} conversion(s) but {len(args)} argument(s) were given")
            return INT
        out = []
        k = 0
        for it in items:
            if it[0] == "lit":
                out.append(it)
                continue
            ch, arg, at = it[1], args[k], arg_types[k]
            k += 1
            ok = (is_error(at)
                  or (ch in "dc" and is_integral(at))
                  or (ch == "f" and at == FLOAT)
                  or (ch == "s" and is_string_like(at)))
            if not ok:
                self.err(arg, f"printf %{ch} cannot print a value of type {at}")
            out.append(("spec", ch, arg))
        n.format_items = out
        return INT

    def call_scanf(self, n):
        items = self.literal_format(n, "scanf")
        args = n.args[1:]
        if items is None:
            for a in args:
                self.expr(a)
            return INT
        specs = [it for it in items if it[0] == "spec"]
        for it in items:
            if it[0] == "lit" and it[1].strip(b" \t\n"):
                self.err(n.args[0], "scanf format may contain only conversions and white space")
                for a in args:
                    self.expr(a)
                return INT
        if len(specs) != len(args):
            self.err(n, f"scanf format has {len(specs)} conversion(s) but {len(args)} argument(s) were given")
            for a in args:
                self.expr(a)
            return INT
        out = []
        # white space before a conversion makes %c skip white space (" %c")
        n.scanf_skip, seen_ws = [], False
        for it in items:
            if it[0] == "lit":
                seen_ws = True
            else:
                n.scanf_skip.append(seen_ws)
                seen_ws = False
        for (_, ch), arg in zip(specs, args):
            if ch == "s":
                at = self.expr(arg)
                if not (is_error(at) or (isinstance(at, ArrayType) and at.elem == CHAR and len(at.dims) == 1
                                         and at.is_complete)):
                    self.err(arg, "scanf %s needs a char array name")
                out.append(("spec", ch, arg))
                continue
            want = {"d": INT, "c": CHAR, "f": FLOAT}[ch]
            if arg.kind != "UnaryOp" or arg.operator != "&":
                self.expr(arg)
                self.err(arg, f"scanf %{ch} needs the address of a variable (write &name)")
                continue
            target = arg.operand
            tt = self.expr(target)
            arg.ctype, arg.const_value, arg.scanf_address = tt, None, True
            if self.check_lvalue(target, tt, "read into") and tt != want:
                self.err(arg, f"scanf %{ch} needs the address of a {want} variable (got {tt})")
            out.append(("spec", ch, target))
        n.format_items = out
        return INT

    def call_atoi(self, n):
        if len(n.args) != 1:
            for a in n.args:
                self.expr(a)
            self.err(n, f"function 'atoi' expects 1 argument but {len(n.args)} were given")
            return INT
        at = self.expr(n.args[0])
        if not is_string_like(at) and not is_error(at):
            self.err(n.args[0], f"argument 1 of 'atoi': cannot pass {at} where char* is expected")
        return INT


# ---------------------------------------------------------------------------
def analyze(program) -> SemanticResult:
    """Analyze a parsed Program. Errors are appended (sorted by line) to
    common.errors.semantic_errors and also returned in the result."""
    return SemanticAnalyzer().run(program)


def format_semantic(result: SemanticResult) -> str:
    """Readable dump of the symbol information (for --semantic)."""
    lines = []

    def table(title, header, rows):
        lines.append(title)
        if not rows:
            lines.append("  (none)")
            lines.append("")
            return
        widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
        fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
        lines.append(fmt.format(*header))
        lines.append("  " + "  ".join("-" * w for w in widths))
        for r in rows:
            lines.append(fmt.format(*[str(c) for c in r]))
        lines.append("")

    table("Global variables", ("name", "type", "size", "offset", "line"),
          [(s.name, s.type, s.size, s.offset, s.line) for s in result.globals])
    table("Functions", ("name", "signature", "frame", "defined", "line"),
          [(name, sym.type, result.functions[name].frame_size if name in result.functions else "-",
            "yes" if sym.defined else "prototype only", sym.line)
           for name, sym in result.table.global_scope.symbols.items() if sym.kind == "func"])
    for name, info in result.functions.items():
        rows = [(s.ir_name, s.name, "param", s.type, s.size, s.offset, s.line) for s in info.params]
        rows += [(s.ir_name, s.name, "local", s.type, s.size, s.offset, s.line) for s in info.locals]
        table(f"Function {name}: parameters and locals (frame size {info.frame_size} bytes)",
              ("ir name", "source", "kind", "type", "size", "offset", "line"), rows)
    table("Typedefs", ("name", "type"), [(n, t) for n, t in result.typedefs])
    table("Enum constants", ("name", "value"), result.enums)
    return "\n".join(lines).rstrip() + "\n"
