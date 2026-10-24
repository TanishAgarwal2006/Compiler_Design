"""
Type objects for semantic analysis .

Types are immutable and compared structurally, so two types are equivalent
exactly when they are built from the same constructors over equivalent types
(structural equivalence). Typedef names never survive into a Type: they are
resolved to their underlying type when the typedef is declared.

Supported types
    int      4 bytes (short, long, signed and unsigned also map here)
    bool     4 bytes holding 0 or 1: any value stored into a bool becomes (value != 0)
    char     1 byte, signed
    float    4 bytes, single precision (double maps here)
    void     only as a function return type or an empty parameter list
    char*    "string": the address of a NUL-terminated byte sequence (4 bytes)
    array    element type plus dimensions; only the first dimension may be
             unknown, and only for parameters or initialised arrays
    function return type plus parameter types
"""
from dataclasses import dataclass
from typing import Optional


class Type:
    """Base class for all types."""


@dataclass(frozen=True)
class BasicType(Type):
    name: str
    width: int

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class StringType(Type):
    width: int = 4

    def __str__(self) -> str:
        return "char*"


@dataclass(frozen=True)
class ErrorType(Type):
    """Result type after an error; compatible with everything so one mistake
    does not produce a cascade of follow-up errors."""
    width: int = 0

    def __str__(self) -> str:
        return "<error>"


@dataclass(frozen=True)
class ArrayType(Type):
    elem: Type
    dims: tuple  # ints; the first entry may be None (unknown size)

    @property
    def width(self) -> int:
        """Bytes of storage. An array whose first dimension is unknown is a
        parameter (or not yet sized) and occupies one address."""
        if self.dims[0] is None:
            return 4
        total = self.elem.width
        for d in self.dims:
            total *= d
        return total

    @property
    def is_complete(self) -> bool:
        return self.dims[0] is not None

    def row_type(self) -> Type:
        """Type of one subscript applied: the sub-array, or the element."""
        if len(self.dims) > 1:
            return ArrayType(self.elem, self.dims[1:])
        return self.elem

    def element_count(self) -> int:
        """Total number of scalar elements (known dimensions only)."""
        total = 1
        for d in self.dims:
            total *= d if d is not None else 1
        return total

    def __str__(self) -> str:
        return f"{self.elem}" + "".join(f"[{'' if d is None else d}]" for d in self.dims)


@dataclass(frozen=True)
class FunctionType(Type):
    ret: Type
    params: tuple
    width: int = 0

    def __str__(self) -> str:
        return f"({', '.join(str(p) for p in self.params)}) -> {self.ret}"


INT = BasicType("int", 4)
CHAR = BasicType("char", 1)
FLOAT = BasicType("float", 4)
BOOL = BasicType("bool", 4)
VOID = BasicType("void", 0)
STRING = StringType()
ERROR = ErrorType()


def is_error(t: Type) -> bool:
    return isinstance(t, ErrorType)


def is_arithmetic(t: Type) -> bool:
    return t in (INT, CHAR, FLOAT, BOOL)


def is_integral(t: Type) -> bool:
    return t in (INT, CHAR, BOOL)


def promote(t: Type) -> Type:
    """Integer promotion: char and bool become int, everything else is unchanged."""
    return INT if t in (CHAR, BOOL) else t


def common_arithmetic(a: Type, b: Type) -> Type:
    """Result type of a binary arithmetic operation: float if either operand
    is float, otherwise int ."""
    if a == FLOAT or b == FLOAT:
        return FLOAT
    return INT


def is_string_like(t: Type) -> bool:
    """A value usable where a string address is expected: a char*, or a
    one-dimensional char array (which decays to its address)."""
    if t == STRING:
        return True
    return isinstance(t, ArrayType) and t.elem == CHAR and len(t.dims) == 1


def assignable(dst: Type, src: Type) -> bool:
    """Can a value of type src be stored into something of type dst?"""
    if is_error(dst) or is_error(src):
        return True
    if is_arithmetic(dst) and is_arithmetic(src):
        return True
    if dst == STRING:
        return is_string_like(src)
    return False


def storage_size(t: Type) -> int:
    return t.width
