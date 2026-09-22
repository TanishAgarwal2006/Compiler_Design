"""
Phase 2 - Syntax Analysis
AST node definitions produced by the parser (parser.py). Each node is a
small dataclass; format_ast() renders a tree for --ast output and for the
phase-2 test harness.
"""
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ASTNode:
    kind: str
    line: Optional[int] = None


@dataclass
class Program(ASTNode):
    declarations: list["ASTNode"] = field(default_factory=list)

    def __init__(self, declarations: list["ASTNode"]):
        super().__init__("Program", None)
        self.declarations = declarations


@dataclass
class TypeSpecifier(ASTNode):
    name: str = ""

    def __init__(self, name: str, line: Optional[int] = None):
        super().__init__("TypeSpecifier", line)
        self.name = name


@dataclass
class ArrayDimension(ASTNode):
    size: Any = None

    def __init__(self, size: Any, line: Optional[int] = None):
        super().__init__("ArrayDimension", line)
        self.size = size

# a declarator can represent a variable, array, function, or function pointer.
# pointer_level counts leading '*' (0 = plain value, 1 = pointer, 2 = pointer-to-pointer, ...).
@dataclass
class Declarator(ASTNode):
    name: str = ""
    kind_name: str = "variable"
    dimensions: list[ArrayDimension] = field(default_factory=list)
    params: Optional[list["Parameter"]] = None
    pointer_level: int = 0
    is_reference: bool = False

    def __init__(
        self,
        name: str,
        kind_name: str = "variable",
        dimensions: Optional[list[ArrayDimension]] = None,
        params: Optional[list["Parameter"]] = None,
        pointer_level: int = 0,
        is_reference: bool = False,
        line: Optional[int] = None,
    ):
        super().__init__("Declarator", line)
        self.name = name
        self.kind_name = kind_name
        self.dimensions = dimensions or []
        self.params = params
        self.pointer_level = pointer_level
        self.is_reference = is_reference


@dataclass
class Parameter(ASTNode):
    type_spec: TypeSpecifier = None
    declarator: Declarator = None

    def __init__(self, type_spec: TypeSpecifier, declarator: Declarator, line: Optional[int] = None):
        super().__init__("Parameter", line)
        self.type_spec = type_spec
        self.declarator = declarator


# Trailing "..." in a parameter list, e.g. "int sum(int count, ...)". Kept as
# its own node (rather than a special Parameter) so a variadic function's
# fixed parameters still classify normally; this marker just records that
# more arguments may follow.
@dataclass
class VarArgsParameter(ASTNode):
    def __init__(self, line: Optional[int] = None):
        super().__init__("VarArgsParameter", line)


@dataclass
class Declaration(ASTNode):
    type_spec: TypeSpecifier = None
    declarators: list["InitDeclarator"] = field(default_factory=list)
    storage: Optional[str] = None

    def __init__(
        self,
        type_spec: TypeSpecifier,
        declarators: list["InitDeclarator"],
        storage: Optional[str] = None,
        line: Optional[int] = None,
    ):
        super().__init__("Declaration", line)
        self.type_spec = type_spec
        self.declarators = declarators
        self.storage = storage


@dataclass
class InitDeclarator(ASTNode):
    declarator: Declarator = None
    initializer: Optional["ASTNode"] = None

    def __init__(self, declarator: Declarator, initializer: Optional["ASTNode"] = None, line: Optional[int] = None):
        super().__init__("InitDeclarator", line)
        self.declarator = declarator
        self.initializer = initializer


@dataclass
class InitializerList(ASTNode):
    values: list["ASTNode"] = field(default_factory=list)

    def __init__(self, values: list["ASTNode"], line: Optional[int] = None):
        super().__init__("InitializerList", line)
        self.values = values

# Function definitions keep the signature separate from the function body.
@dataclass
class FunctionDefinition(ASTNode):
    return_type: TypeSpecifier = None
    declarator: Declarator = None
    body: "CompoundStatement" = None
    storage: Optional[str] = None

    def __init__(
        self,
        return_type: TypeSpecifier,
        declarator: Declarator,
        body: "CompoundStatement",
        storage: Optional[str] = None,
        line: Optional[int] = None,
    ):
        super().__init__("FunctionDefinition", line)
        self.return_type = return_type
        self.declarator = declarator
        self.body = body
        self.storage = storage


@dataclass
class CompoundStatement(ASTNode):
    items: list["ASTNode"] = field(default_factory=list)

    def __init__(self, items: list["ASTNode"], line: Optional[int] = None):
        super().__init__("CompoundStatement", line)
        self.items = items


@dataclass
class IfStatement(ASTNode):
    condition: "ASTNode" = None
    then_branch: "ASTNode" = None
    else_branch: Optional["ASTNode"] = None

    def __init__(self, condition: "ASTNode", then_branch: "ASTNode", else_branch: Optional["ASTNode"] = None, line: Optional[int] = None):
        super().__init__("IfStatement", line)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


@dataclass
class WhileStatement(ASTNode):
    condition: "ASTNode" = None
    body: "ASTNode" = None

    def __init__(self, condition: "ASTNode", body: "ASTNode", line: Optional[int] = None):
        super().__init__("WhileStatement", line)
        self.condition = condition
        self.body = body


@dataclass
class DoWhileStatement(ASTNode):
    body: "ASTNode" = None
    condition: "ASTNode" = None

    def __init__(self, body: "ASTNode", condition: "ASTNode", line: Optional[int] = None):
        super().__init__("DoWhileStatement", line)
        self.body = body
        self.condition = condition


@dataclass
class UntilStatement(ASTNode):
    """"until (cond) stmt" - sugar for "while (!cond) stmt", repeats while
    the condition is FALSE. Kept as a distinct node (rather than negating
    into WhileStatement at parse time) so --ast output reflects what the
    programmer actually wrote."""
    condition: "ASTNode" = None
    body: "ASTNode" = None

    def __init__(self, condition: "ASTNode", body: "ASTNode", line: Optional[int] = None):
        super().__init__("UntilStatement", line)
        self.condition = condition
        self.body = body


@dataclass
class DoUntilStatement(ASTNode):
    """"do stmt until (cond);" - sugar for "do stmt while (!cond);"."""
    body: "ASTNode" = None
    condition: "ASTNode" = None

    def __init__(self, body: "ASTNode", condition: "ASTNode", line: Optional[int] = None):
        super().__init__("DoUntilStatement", line)
        self.body = body
        self.condition = condition


@dataclass
class ForStatement(ASTNode):
    init: Optional["ASTNode"] = None
    condition: Optional["ASTNode"] = None
    update: Optional["ASTNode"] = None
    body: "ASTNode" = None

    def __init__(
        self,
        init: Optional["ASTNode"],
        condition: Optional["ASTNode"],
        update: Optional["ASTNode"],
        body: "ASTNode",
        line: Optional[int] = None,
    ):
        super().__init__("ForStatement", line)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body


@dataclass
class ReturnStatement(ASTNode):
    value: Optional["ASTNode"] = None

    def __init__(self, value: Optional["ASTNode"] = None, line: Optional[int] = None):
        super().__init__("ReturnStatement", line)
        self.value = value


@dataclass
class JumpStatement(ASTNode):
    keyword: str = ""
    target: Optional[str] = None

    def __init__(self, keyword: str, target: Optional[str] = None, line: Optional[int] = None):
        super().__init__("JumpStatement", line)
        self.keyword = keyword
        self.target = target


@dataclass
class LabeledStatement(ASTNode):
    label: str = ""
    statement: "ASTNode" = None

    def __init__(self, label: str, statement: "ASTNode", line: Optional[int] = None):
        super().__init__("LabeledStatement", line)
        self.label = label
        self.statement = statement

# Optional expression also represents empty statements (;).
@dataclass
class ExpressionStatement(ASTNode):
    expression: Optional["ASTNode"] = None

    def __init__(self, expression: Optional["ASTNode"] = None, line: Optional[int] = None):
        super().__init__("ExpressionStatement", line)
        self.expression = expression


@dataclass
class Identifier(ASTNode):
    name: str = ""

    def __init__(self, name: str, line: Optional[int] = None):
        super().__init__("Identifier", line)
        self.name = name


@dataclass
class Literal(ASTNode):
    literal_type: str = ""
    value: Any = None

    def __init__(self, literal_type: str, value: Any, line: Optional[int] = None):
        super().__init__("Literal", line)
        self.literal_type = literal_type
        self.value = value


@dataclass
class BinaryOp(ASTNode):
    operator: str = ""
    left: "ASTNode" = None
    right: "ASTNode" = None

    def __init__(self, operator: str, left: "ASTNode", right: "ASTNode", line: Optional[int] = None):
        super().__init__("BinaryOp", line)
        self.operator = operator
        self.left = left
        self.right = right


@dataclass
class UnaryOp(ASTNode):
    operator: str = ""
    operand: "ASTNode" = None
    position: str = "prefix"

    def __init__(self, operator: str, operand: "ASTNode", position: str = "prefix", line: Optional[int] = None):
        super().__init__("UnaryOp", line)
        self.operator = operator
        self.operand = operand
        self.position = position


@dataclass
class ConditionalExpression(ASTNode):
    """Ternary "cond ? then_value : else_value"."""
    condition: "ASTNode" = None
    then_value: "ASTNode" = None
    else_value: "ASTNode" = None

    def __init__(self, condition: "ASTNode", then_value: "ASTNode", else_value: "ASTNode", line: Optional[int] = None):
        super().__init__("ConditionalExpression", line)
        self.condition = condition
        self.then_value = then_value
        self.else_value = else_value


@dataclass
class CastExpression(ASTNode):
    """"(type ***) expr" - a type cast, most commonly seen wrapping the
    result of malloc/calloc/realloc for dynamic memory allocation."""
    type_spec: TypeSpecifier = None
    pointer_level: int = 0
    operand: "ASTNode" = None

    def __init__(self, type_spec: TypeSpecifier, pointer_level: int, operand: "ASTNode", line: Optional[int] = None):
        super().__init__("CastExpression", line)
        self.type_spec = type_spec
        self.pointer_level = pointer_level
        self.operand = operand


@dataclass
class Assignment(ASTNode):
    operator: str = ""
    target: "ASTNode" = None
    value: "ASTNode" = None

    def __init__(self, operator: str, target: "ASTNode", value: "ASTNode", line: Optional[int] = None):
        super().__init__("Assignment", line)
        self.operator = operator
        self.target = target
        self.value = value


@dataclass
class FunctionCall(ASTNode):
    callee: "ASTNode" = None
    args: list["ASTNode"] = field(default_factory=list)

    def __init__(self, callee: "ASTNode", args: list["ASTNode"], line: Optional[int] = None):
        super().__init__("FunctionCall", line)
        self.callee = callee
        self.args = args


@dataclass
class ArrayAccess(ASTNode):
    array: "ASTNode" = None
    index: "ASTNode" = None

    def __init__(self, array: "ASTNode", index: "ASTNode", line: Optional[int] = None):
        super().__init__("ArrayAccess", line)
        self.array = array
        self.index = index


# struct/union member access: expr.member (is_pointer=False) or expr->member (is_pointer=True)
@dataclass
class MemberAccess(ASTNode):
    target: "ASTNode" = None
    member: str = ""
    is_pointer: bool = False

    def __init__(self, target: "ASTNode", member: str, is_pointer: bool = False, line: Optional[int] = None):
        super().__init__("MemberAccess", line)
        self.target = target
        self.member = member
        self.is_pointer = is_pointer


# struct/union specifier: tag is the optional name, members is None for a bare
# reference (e.g. "struct Point p;"), else a list of Declaration nodes.
@dataclass
class StructSpecifier(ASTNode):
    tag: Optional[str] = None
    members: Optional[list["Declaration"]] = None
    is_union: bool = False

    def __init__(
        self,
        tag: Optional[str],
        members: Optional[list["Declaration"]] = None,
        is_union: bool = False,
        line: Optional[int] = None,
    ):
        super().__init__("UnionSpecifier" if is_union else "StructSpecifier", line)
        self.tag = tag
        self.members = members
        self.is_union = is_union


@dataclass
class Enumerator(ASTNode):
    name: str = ""
    value: Optional["ASTNode"] = None

    def __init__(self, name: str, value: Optional["ASTNode"] = None, line: Optional[int] = None):
        super().__init__("Enumerator", line)
        self.name = name
        self.value = value


@dataclass
class EnumSpecifier(ASTNode):
    tag: Optional[str] = None
    enumerators: Optional[list[Enumerator]] = None

    def __init__(self, tag: Optional[str], enumerators: Optional[list[Enumerator]] = None, line: Optional[int] = None):
        super().__init__("EnumSpecifier", line)
        self.tag = tag
        self.enumerators = enumerators


@dataclass
class SwitchCase(ASTNode):
    # value is None for the "default" case
    value: Optional["ASTNode"] = None
    body: list["ASTNode"] = field(default_factory=list)

    def __init__(self, value: Optional["ASTNode"], body: list["ASTNode"], line: Optional[int] = None):
        super().__init__("SwitchCase", line)
        self.value = value
        self.body = body


@dataclass
class SwitchStatement(ASTNode):
    expression: "ASTNode" = None
    cases: list[SwitchCase] = field(default_factory=list)

    def __init__(self, expression: "ASTNode", cases: list[SwitchCase], line: Optional[int] = None):
        super().__init__("SwitchStatement", line)
        self.expression = expression
        self.cases = cases


def format_ast(node: Any, indent: int = 0) -> str:
    prefix = "  " * indent

    if node is None:
        return f"{prefix}None"

    if isinstance(node, list):
        if not node:
            return f"{prefix}[]"
        lines = [f"{prefix}["]
        for item in node:
            lines.append(format_ast(item, indent + 1) + ",")
        lines.append(f"{prefix}]")
        return "\n".join(lines)

    if isinstance(node, ASTNode):
        fields = []
        for key, value in vars(node).items():
            if key == "kind":
                continue
            if value is None or value == []:
                continue
            # pointer_level defaults to 0 for every declarator; only show it
            # when the declarator is actually a pointer, to keep plain
            # variable/array/function declarators printing as before.
            if key == "pointer_level" and value == 0:
                continue
            if key == "is_reference" and value is False:
                continue
            if isinstance(value, (ASTNode, list)):
                fields.append(f"{prefix}  {key}:\n{format_ast(value, indent + 2)}")
            else:
                fields.append(f"{prefix}  {key}: {value}")

        if not fields:
            return f"{prefix}{node.kind}"

        return "\n".join([f"{prefix}{node.kind}"] + fields)

    return f"{prefix}{node}"

# ---------------------------------------------------------------------------
# C++ subset nodes (classes, access control, free store)
# ---------------------------------------------------------------------------

@dataclass
class AccessLabel(ASTNode):
    """An access label inside a class/struct body, e.g. "public:". It applies
    to every member declared after it until the next label."""
    access: str = "private"

    def __init__(self, access: str, line: Optional[int] = None):
        super().__init__("AccessLabel", line)
        self.access = access


@dataclass
class BaseSpecifier(ASTNode):
    """One entry of an inheritance list, e.g. the "public Animal" in
    "class Dog : public Animal"."""
    name: str = ""
    access: str = "private"

    def __init__(self, name: str, access: str = "private", line: Optional[int] = None):
        super().__init__("BaseSpecifier", line)
        self.name = name
        self.access = access


@dataclass
class ClassSpecifier(ASTNode):
    """tag is the class name; bases is the inheritance list; members is None
    for a bare reference ("class Node n;") and a list otherwise."""
    tag: Optional[str] = None
    bases: list["BaseSpecifier"] = field(default_factory=list)
    members: Optional[list["ASTNode"]] = None

    def __init__(
        self,
        tag: Optional[str],
        bases: Optional[list["BaseSpecifier"]] = None,
        members: Optional[list["ASTNode"]] = None,
        line: Optional[int] = None,
    ):
        super().__init__("ClassSpecifier", line)
        self.tag = tag
        self.bases = bases or []
        self.members = members


@dataclass
class NewExpression(ASTNode):
    """"new T", "new T[n]" or "new T(args)" - dynamic allocation."""
    type_spec: Any = None
    count: Optional["ASTNode"] = None
    args: Optional[list["ASTNode"]] = None

    def __init__(self, type_spec, count=None, args=None, line: Optional[int] = None):
        super().__init__("NewExpression", line)
        self.type_spec = type_spec
        self.count = count
        self.args = args


@dataclass
class DeleteExpression(ASTNode):
    """"delete p" or "delete[] p"."""
    operand: "ASTNode" = None
    is_array: bool = False

    def __init__(self, operand: "ASTNode", is_array: bool = False, line: Optional[int] = None):
        super().__init__("DeleteExpression", line)
        self.operand = operand
        self.is_array = is_array


@dataclass
class QualifiedName(ASTNode):
    """"ClassName::member" - scope-resolved access to a static member or a
    base class's member, e.g. "Animal::legs" or "Base::greet()"."""
    scope: str = ""
    name: str = ""

    def __init__(self, scope: str, name: str, line: Optional[int] = None):
        super().__init__("QualifiedName", line)
        self.scope = scope
        self.name = name
