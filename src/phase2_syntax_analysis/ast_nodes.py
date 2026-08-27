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


@dataclass
class Declarator(ASTNode):
    name: str = ""
    kind_name: str = "variable"
    dimensions: list[ArrayDimension] = field(default_factory=list)
    params: Optional[list["Parameter"]] = None

    def __init__(
        self,
        name: str,
        kind_name: str = "variable",
        dimensions: Optional[list[ArrayDimension]] = None,
        params: Optional[list["Parameter"]] = None,
        line: Optional[int] = None,
    ):
        super().__init__("Declarator", line)
        self.name = name
        self.kind_name = kind_name
        self.dimensions = dimensions or []
        self.params = params


@dataclass
class Parameter(ASTNode):
    type_spec: TypeSpecifier = None
    declarator: Declarator = None

    def __init__(self, type_spec: TypeSpecifier, declarator: Declarator, line: Optional[int] = None):
        super().__init__("Parameter", line)
        self.type_spec = type_spec
        self.declarator = declarator


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


@dataclass
class FunctionDefinition(ASTNode):
    return_type: TypeSpecifier = None
    declarator: Declarator = None
    body: "CompoundStatement" = None

    def __init__(
        self,
        return_type: TypeSpecifier,
        declarator: Declarator,
        body: "CompoundStatement",
        line: Optional[int] = None,
    ):
        super().__init__("FunctionDefinition", line)
        self.return_type = return_type
        self.declarator = declarator
        self.body = body


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
            if isinstance(value, (ASTNode, list)):
                fields.append(f"{prefix}  {key}:\n{format_ast(value, indent + 2)}")
            else:
                fields.append(f"{prefix}  {key}: {value}")

        if not fields:
            return f"{prefix}{node.kind}"

        return "\n".join([f"{prefix}{node.kind}"] + fields)

    return f"{prefix}{node}"
