from dataclasses import dataclass
from typing import Dict, List, Tuple
from phase2_syntax_analysis import ast_nodes as N

_ROLE_PRIORITY = ["function", "array", "parameter", "typedef", "label", "variable"]


@dataclass
class SymbolRecord:
    name: str
    role: str
    data_type: str = "int"
    scope: str = "global"
    details: str = ""


class SymbolClassifier:
    def __init__(self):
        self.roles: Dict[str, str] = {}
        self.records: Dict[str, SymbolRecord] = {}

    def _set(self, name: str, role: str, data_type: str = "int", scope: str = "global", details: str = ""):
        existing = self.roles.get(name)
        if existing is None:
            self.roles[name] = role
            self.records[name] = SymbolRecord(name, role, data_type, scope, details)
            return

        if _ROLE_PRIORITY.index(role) <= _ROLE_PRIORITY.index(existing):
            self.roles[name] = role
            rec = self.records[name]
            rec.role = role
            if data_type != "int" or rec.data_type == "int":
                rec.data_type = data_type
            if rec.scope == "global" or scope == "global":
                rec.scope = "global"
            elif not rec.scope:
                rec.scope = scope
            if details and not rec.details:
                rec.details = details

    def classify(self, program: N.Program) -> Dict[str, str]:
        for decl in program.declarations:
            self._visit_external(decl)
        return self.roles

    def classify_detailed(self, program: N.Program) -> Dict[str, SymbolRecord]:
        self.classify(program)
        return self.records

    def _visit_external(self, node):
        if isinstance(node, N.FunctionDefinition):
            fn_name = node.declarator.name
            ret_type = node.return_type.name if node.return_type else "int"
            params_str = "()"
            if node.declarator.params:
                p_types = [p.type_spec.name if p.type_spec else "int" for p in node.declarator.params]
                params_str = f"({', '.join(p_types)})"

            self._set(fn_name, "function", data_type=ret_type, scope="global", details=f"params: {params_str}")
            current_scope = f"function:{fn_name}"
            for param in node.declarator.params or []:
                p_name = param.declarator.name
                p_type = param.type_spec.name if param.type_spec else "int"
                self._set(p_name, "parameter", data_type=p_type, scope=current_scope)
            self._visit_stmt(node.body, scope=current_scope)
        elif isinstance(node, N.Declaration):
            self._visit_declaration(node, scope="global")

    def _visit_declaration(self, decl: N.Declaration, scope: str = "global"):
        role_if_plain = "typedef" if decl.storage == "typedef" else "variable"
        type_name = decl.type_spec.name if decl.type_spec else "int"

        for init_decl in decl.declarators:
            d = init_decl.declarator
            details = ""
            if d.kind_name == "function":
                role = "function"
                details = "params: ()"
            elif d.kind_name == "array":
                role = "array"
                dim_str = "".join([f"[{dim.size.value if hasattr(dim.size, 'value') else ''}]" for dim in d.dimensions])
                details = f"dims: {dim_str}" if dim_str else "array"
            else:
                role = role_if_plain

            self._set(d.name, role, data_type=type_name, scope=scope, details=details)
            if init_decl.initializer is not None:
                self._visit_expr(init_decl.initializer, scope=scope)

    def _visit_stmt(self, node, scope: str = "global"):
        if node is None:
            return
        if isinstance(node, N.CompoundStatement):
            for item in node.items:
                self._visit_stmt(item, scope=scope)
        elif isinstance(node, N.Declaration):
            self._visit_declaration(node, scope=scope)
        elif isinstance(node, N.IfStatement):
            self._visit_expr(node.condition, scope=scope)
            self._visit_stmt(node.then_branch, scope=scope)
            self._visit_stmt(node.else_branch, scope=scope)
        elif isinstance(node, N.WhileStatement):
            self._visit_expr(node.condition, scope=scope)
            self._visit_stmt(node.body, scope=scope)
        elif isinstance(node, N.DoWhileStatement):
            self._visit_stmt(node.body, scope=scope)
            self._visit_expr(node.condition, scope=scope)
        elif isinstance(node, N.ForStatement):
            self._visit_expr(node.init, scope=scope)
            self._visit_expr(node.condition, scope=scope)
            self._visit_expr(node.update, scope=scope)
            self._visit_stmt(node.body, scope=scope)
        elif isinstance(node, N.ReturnStatement):
            self._visit_expr(node.value, scope=scope)
        elif isinstance(node, N.JumpStatement):
            if node.keyword == "goto" and node.target:
                self._set(node.target, "label", data_type="void", scope=scope)
        elif isinstance(node, N.LabeledStatement):
            self._set(node.label, "label", data_type="void", scope=scope)
            self._visit_stmt(node.statement, scope=scope)
        elif isinstance(node, N.ExpressionStatement):
            self._visit_expr(node.expression, scope=scope)

    def _visit_expr(self, node, scope: str = "global"):
        if node is None:
            return
        if isinstance(node, N.Identifier):
            self._set(node.name, "variable", scope=scope)
        elif isinstance(node, N.BinaryOp):
            self._visit_expr(node.left, scope=scope)
            self._visit_expr(node.right, scope=scope)
        elif isinstance(node, N.UnaryOp):
            self._visit_expr(node.operand, scope=scope)
        elif isinstance(node, N.Assignment):
            self._visit_expr(node.target, scope=scope)
            self._visit_expr(node.value, scope=scope)
        elif isinstance(node, N.FunctionCall):
            if isinstance(node.callee, N.Identifier):
                callee_name = node.callee.name
                if callee_name in ("printf", "scanf"):
                    self._set(callee_name, "function", data_type="int", scope="global", details="params: (format, ...)")
                else:
                    self._set(callee_name, "function", scope=scope)
            else:
                self._visit_expr(node.callee, scope=scope)
            for arg in node.args:
                self._visit_expr(arg, scope=scope)
        elif isinstance(node, N.ArrayAccess):
            if isinstance(node.array, N.Identifier):
                self._set(node.array.name, "array", scope=scope)
            else:
                self._visit_expr(node.array, scope=scope)
            self._visit_expr(node.index, scope=scope)
        elif isinstance(node, N.InitializerList):
            for value in node.values:
                self._visit_expr(value, scope=scope)


def classify_program(program: N.Program) -> Dict[str, str]:
    return SymbolClassifier().classify(program)


def classify_program_detailed(program: N.Program) -> Dict[str, SymbolRecord]:
    return SymbolClassifier().classify_detailed(program)


def format_symbol_table(program: N.Program) -> str:
    records = classify_program_detailed(program)
    if not records:
        return "(no identifiers declared)"
    lines = [f"{'Identifier':<20} {'Role':<12} {'Type':<10} {'Scope':<22} {'Details':<20}", "-" * 84]
    for name, rec in sorted(records.items()):
        lines.append(f"{rec.name:<20} {rec.role:<12} {rec.data_type:<10} {rec.scope:<22} {rec.details:<20}")
    return "\n".join(lines)


def enrich_tokens(token_rows: List[Tuple[str, str]], program: N.Program) -> List[Tuple[str, str]]:
    records = classify_program_detailed(program)
    enriched = []
    role_map = {
        "FUNCTION": "FUNCTION_NAME",
        "VARIABLE": "VARIABLE_NAME",
        "PARAMETER": "PARAMETER_NAME",
        "ARRAY": "ARRAY_NAME",
        "TYPEDEF": "TYPENAME",
        "LABEL": "LABEL_NAME",
    }
    for lexeme, token_type in token_rows:
        if token_type == "IDENTIFIER" and lexeme in records:
            role = records[lexeme].role.upper()
            new_type = role_map.get(role, token_type)
            enriched.append((lexeme, new_type))
        else:
            enriched.append((lexeme, token_type))
    return enriched


def format_enriched_token_table(token_rows: List[Tuple[str, str]], program: N.Program) -> str:
    enriched = enrich_tokens(token_rows, program)
    lines = [f"{'Token':<25} {'Token_Type':<25}", "-" * 50]
    for lexeme, token_name in enriched:
        lines.append(f"{str(lexeme):<25} {token_name:<25}")
    return "\n".join(lines)
