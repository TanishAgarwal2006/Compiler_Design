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

        def rank(r: str) -> int:
            # unknown roles sort last instead of raising ValueError
            return _ROLE_PRIORITY.index(r) if r in _ROLE_PRIORITY else len(_ROLE_PRIORITY)

        if rank(role) <= rank(existing):
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
            ret_type = self._describe_type(node.return_type)
            params_str = "()"
            if node.declarator.params:
                p_types = [
                    "..." if isinstance(p, N.VarArgsParameter) else self._describe_type(p.type_spec)
                    for p in node.declarator.params
                ]
                params_str = f"({', '.join(p_types)})"

            storage_prefix = "static " if getattr(node, "storage", None) == "static" else ""
            self._set(fn_name, "function", data_type=ret_type, scope="global", details=f"{storage_prefix}params: {params_str}")
            current_scope = f"function:{fn_name}"
            for param in node.declarator.params or []:
                if isinstance(param, N.VarArgsParameter):
                    continue
                if param.declarator is None:
                    # Unnamed/abstract parameter (e.g. "int f(int);" or the
                    # sole "void" in "int f(void)") - nothing to name, so
                    # there's no symbol table entry to add for it.
                    continue
                p_name = param.declarator.name
                p_type = self._describe_type(param.type_spec)
                pointer_prefix = "*" * getattr(param.declarator, "pointer_level", 0)
                self._set(
                    p_name,
                    "parameter",
                    data_type=p_type,
                    scope=current_scope,
                    details=f"pointer ({pointer_prefix}{p_name})" if pointer_prefix else "",
                )
            self._visit_stmt(node.body, scope=current_scope)
        elif isinstance(node, N.Declaration):
            self._visit_declaration(node, scope="global")

    def _visit_declaration(self, decl: N.Declaration, scope: str = "global"):
        role_if_plain = "typedef" if decl.storage == "typedef" else "variable"
        storage_prefix = "static " if decl.storage == "static" else ""
        type_spec = decl.type_spec
        type_name = type_spec.name if isinstance(type_spec, N.TypeSpecifier) else self._describe_type(type_spec)

        # struct/union bodies and enum bodies declare their own members/constants;
        # visit those even when the declaration itself introduces no variable
        # (e.g. "struct Point { ... };").
        if isinstance(type_spec, N.StructSpecifier) and type_spec.members:
            struct_scope = f"struct:{type_spec.tag}" if type_spec.tag else "struct:<anonymous>"
            for member in type_spec.members:
                self._visit_member(member, struct_scope)
        elif isinstance(type_spec, N.ClassSpecifier) and type_spec.members:
            class_scope = f"class:{type_spec.tag}" if type_spec.tag else "class:<anonymous>"
            for member in type_spec.members:
                self._visit_member(member, class_scope)
        elif isinstance(type_spec, N.EnumSpecifier) and type_spec.enumerators:
            for enumerator in type_spec.enumerators:
                self._set(enumerator.name, "variable", data_type="int", scope="global", details="enum constant")
                if enumerator.value is not None:
                    self._visit_expr(enumerator.value, scope=scope)

        for init_decl in decl.declarators:
            d = init_decl.declarator
            details = ""
            pointer_prefix = "*" * getattr(d, "pointer_level", 0)
            if d.kind_name in ("function", "function_pointer"):
                role = "function"
                details = "function pointer" if d.kind_name == "function_pointer" else "params: ()"
            elif d.kind_name == "array":
                role = "array"
                dim_str = "".join([f"[{dim.size.value if hasattr(dim.size, 'value') else ''}]" for dim in d.dimensions])
                details = f"dims: {dim_str}" if dim_str else "array"
            elif pointer_prefix:
                role = role_if_plain
                details = f"{storage_prefix}pointer ({pointer_prefix}{d.name})"
            else:
                role = role_if_plain
                details = storage_prefix.strip()

            self._set(d.name, role, data_type=type_name, scope=scope, details=details)
            if init_decl.initializer is not None:
                self._visit_expr(init_decl.initializer, scope=scope)

    def _visit_member(self, member, scope: str):
        """A struct/class member is a declaration, an inline member function,
        or an access label ("public:"), which declares no identifier."""
        if isinstance(member, N.AccessLabel):
            return
        if isinstance(member, N.FunctionDefinition):
            self._visit_external(member)
            return
        if isinstance(member, N.Declaration):
            self._visit_declaration(member, scope=scope)

    @staticmethod
    def _describe_type(type_spec) -> str:
        if type_spec is None:
            return "int"
        if isinstance(type_spec, N.ClassSpecifier):
            return f"class {type_spec.tag}" if type_spec.tag else "class"
        if isinstance(type_spec, N.StructSpecifier):
            kind = "union" if type_spec.is_union else "struct"
            return f"{kind} {type_spec.tag}" if type_spec.tag else kind
        if isinstance(type_spec, N.EnumSpecifier):
            return f"enum {type_spec.tag}" if type_spec.tag else "enum"
        return getattr(type_spec, "name", "int")

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
        elif isinstance(node, N.UntilStatement):
            self._visit_expr(node.condition, scope=scope)
            self._visit_stmt(node.body, scope=scope)
        elif isinstance(node, N.DoUntilStatement):
            self._visit_stmt(node.body, scope=scope)
            self._visit_expr(node.condition, scope=scope)
        elif isinstance(node, N.ForStatement):
            # "for (int i = 0; ...)" puts a Declaration in the init slot
            if isinstance(node.init, N.Declaration):
                self._visit_declaration(node.init, scope=scope)
            else:
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
        elif isinstance(node, N.SwitchStatement):
            self._visit_expr(node.expression, scope=scope)
            for case in node.cases:
                if case.value is not None:
                    self._visit_expr(case.value, scope=scope)
                for item in case.body:
                    self._visit_stmt(item, scope=scope)

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
        elif isinstance(node, N.MemberAccess):
            # the member name lives in the struct/union's own namespace, not the
            # identifier table, so only the base expression is classified here.
            self._visit_expr(node.target, scope=scope)
        elif isinstance(node, N.ConditionalExpression):
            self._visit_expr(node.condition, scope=scope)
            self._visit_expr(node.then_value, scope=scope)
            self._visit_expr(node.else_value, scope=scope)
        elif isinstance(node, N.CastExpression):
            self._visit_expr(node.operand, scope=scope)
        elif isinstance(node, N.NewExpression):
            # type_spec is a type name, not an identifier reference, so only
            # the array-size and constructor-argument expressions are visited.
            if node.count is not None:
                self._visit_expr(node.count, scope=scope)
            if node.args:
                for arg in node.args:
                    self._visit_expr(arg, scope=scope)
        elif isinstance(node, N.DeleteExpression):
            self._visit_expr(node.operand, scope=scope)
        elif isinstance(node, N.QualifiedName):
            # "ClassName::member" - the class name is a type, not a variable
            # reference, so nothing new is registered here.
            pass


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