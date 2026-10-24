"""
Scoped symbol table.

Scopes nest: global -> function (parameters and the outermost block) ->
block. `lookup` returns the most recently declared entry visible from the
current scope, so inner declarations shadow outer ones.

Every variable gets a unique IR name so that shadowing never reaches the
TAC: the first `x` in a function is `x`, a shadowing one becomes `x.1`, and a
local that would clash with a global is renamed the same way.

Storage: each symbol gets a size in bytes and an offset aligned to 4. Local
and parameter offsets are relative to the function frame; global offsets are
relative to the start of the data area.
"""
from dataclasses import dataclass, field
from typing import Any, Optional

from .type_system import Type

ALIGN = 4


def align(n: int, to: int = ALIGN) -> int:
    return (n + to - 1) // to * to


@dataclass
class Symbol:
    name: str
    kind: str                 # var, param, func, enum_const, typedef
    type: Type
    line: int = 0
    ir_name: str = ""
    scope: str = "global"     # global, local, param
    size: int = 0
    offset: int = 0
    is_const: bool = False
    const_value: Any = None   # known value of a const scalar or enum constant
    defined: bool = False     # functions: a body has been seen
    storage: Optional[str] = None
    owner: Optional[str] = None  # name of the enclosing function, if any


@dataclass
class Scope:
    kind: str                 # global, function, block
    parent: Optional["Scope"] = None
    symbols: dict = field(default_factory=dict)


@dataclass
class FunctionInfo:
    symbol: Symbol
    params: list = field(default_factory=list)   # parameter Symbols in order
    locals: list = field(default_factory=list)   # local variable Symbols in declaration order
    frame_size: int = 0
    used_names: set = field(default_factory=set)
    locals_started: bool = False  # False while parameters are being declared


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current = self.global_scope
        self.functions: dict = {}          # name -> FunctionInfo, in definition order
        self.globals: list = []            # global variable Symbols in declaration order
        self.enum_tags: set = set()
        self.data_size = 0
        self._fn: Optional[FunctionInfo] = None

    # --- scopes -----------------------------------------------------------
    def push(self, kind: str = "block") -> Scope:
        self.current = Scope(kind, self.current)
        return self.current

    def pop(self) -> None:
        assert self.current.parent is not None, "cannot pop the global scope"
        self.current = self.current.parent

    def lookup(self, name: str) -> Optional[Symbol]:
        scope = self.current
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def lookup_global(self, name: str) -> Optional[Symbol]:
        return self.global_scope.symbols.get(name)

    def declare(self, sym: Symbol) -> Optional[Symbol]:
        """Enter sym in the current scope. Returns the existing entry if the
        name is already declared in this same scope (and enters nothing)."""
        existing = self.current.symbols.get(sym.name)
        if existing is not None:
            return existing
        sym.scope = self._storage_class()
        sym.owner = self._fn.symbol.name if self._fn else None
        self.current.symbols[sym.name] = sym
        return None

    def _storage_class(self) -> str:
        if self._fn is None:
            return "global"
        return "param" if self.current.kind == "function" and not self._fn.locals_started else "local"

    # --- functions --------------------------------------------------------
    def begin_function(self, sym: Symbol) -> FunctionInfo:
        info = FunctionInfo(sym)
        info.used_names = set(self.global_scope.symbols.keys())
        self.functions[sym.name] = info
        self._fn = info
        return info

    def mark_body_started(self) -> None:
        if self._fn:
            self._fn.locals_started = True

    def end_function(self) -> None:
        if self._fn:
            self._fn.frame_size = align(self._fn.frame_size)
        self._fn = None

    # --- storage ----------------------------------------------------------
    def allocate(self, sym: Symbol) -> None:
        """Give a declared variable or parameter its IR name, size and offset."""
        sym.size = sym.type.width
        if self._fn is None:
            sym.ir_name = sym.name
            sym.offset = align(self.data_size)
            self.data_size = sym.offset + align(sym.size)
            self.globals.append(sym)
            return
        fn = self._fn
        sym.ir_name = self._unique(fn, sym.name)
        sym.offset = align(fn.frame_size)
        fn.frame_size = sym.offset + align(sym.size)
        (fn.params if sym.scope == "param" else fn.locals).append(sym)

    @staticmethod
    def _unique(fn: FunctionInfo, name: str) -> str:
        if name not in fn.used_names:
            fn.used_names.add(name)
            return name
        k = 1
        while f"{name}.{k}" in fn.used_names:
            k += 1
        unique = f"{name}.{k}"
        fn.used_names.add(unique)
        return unique

    def resize(self, sym: Symbol, new_type: Type) -> None:
        """Change the type of a not-yet-allocated symbol (array size inferred
        from its initializer)."""
        sym.type = new_type
