"""Coverage audit: is every token type, keyword, AST node class and error message hit by some test?

    python3 tools/coverage_audit.py        (exit 0 only when nothing is missed)

It runs every test/**/*.c file and every unit test in-process and reports what was never exercised:
  tokens   - each name in token_defs.tokens, and each keyword spelling in token_defs.reserved
  nodes    - each class in ast_nodes.py (must be built by the parser at least once)
  errors   - each source line that reports an error (add_*_error, self.err, self.unsupported, GenError, IRError, RunError)
"""
import ast
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from phase1_lexical_analysis import token_defs  # noqa: E402
from phase2_syntax_analysis import ast_nodes  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402
from phase3_intermediate_code import semantic_analyzer as sem  # noqa: E402
from phase3_intermediate_code.ir_generator import generate, GenError  # noqa: E402
from common import errors  # noqa: E402

ERROR_CALLS = {"add_lex_error", "add_syntax_error", "add_semantic_error", "err", "unsupported", "GenError",
               "IRError", "RunError"}


def error_lines():
    """{(file, call line): statement line} of every statement in src/ that reports an error."""
    found = {}
    for path in SRC.rglob("*.py"):
        if path.name == "errors.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for stmt in ast.walk(tree):
            if not isinstance(stmt, ast.stmt):
                continue
            for call in ast.walk(stmt):
                if isinstance(call, ast.Call):
                    f = call.func
                    name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                    if name in ERROR_CALLS:
                        found[(str(path), call.lineno)] = stmt.lineno
    return found


hit_lines, tokens_seen, lexemes_seen, nodes_seen = set(), set(), set(), set()


def tracer(frame, event, arg):
    if not frame.f_code.co_filename.startswith(str(SRC)):
        return None
    if event == "line":
        hit_lines.add((frame.f_code.co_filename, frame.f_lineno))
    return tracer


def wrap_tokens():
    import ply.lex as lex
    orig = lex.Lexer.token

    def token(self):
        t = orig(self)
        if t is not None:
            tokens_seen.add(t.type)
            lexemes_seen.add(str(t.value))
        return t
    lex.Lexer.token = token


def node_classes():
    return {n: c for n, c in vars(ast_nodes).items()
            if isinstance(c, type) and issubclass(c, ast_nodes.ASTNode) and c is not ast_nodes.ASTNode}


def wrap_nodes():
    for name, cls in node_classes().items():
        orig = cls.__init__

        def init(self, *a, _o=orig, _n=name, **k):
            nodes_seen.add(_n)
            _o(self, *a, **k)
        cls.__init__ = init


def compile_file(path):
    from main import tokenize_source
    errors.clear_errors()
    code = path.read_text(encoding="utf-8")
    tokenize_source(code)
    if errors.lex_errors:
        return
    tree = parse_source(code)
    if errors.lex_errors or errors.syntax_errors or tree is None:
        return
    result = sem.analyze(tree)
    if errors.semantic_errors:
        return
    try:
        generate(tree, result)
    except GenError:
        pass


def run_unit_tests():
    for path in sorted((ROOT / "test" / "unit").glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for n in sorted(x for x in dir(mod) if x.startswith("test_")):
            try:
                getattr(mod, n)()
            except Exception:
                pass


def main():
    wrap_tokens()
    wrap_nodes()
    sys.settrace(tracer)
    for path in sorted((ROOT / "test").rglob("*.c")):
        compile_file(path)
    run_unit_tests()
    sys.settrace(None)

    missing = {
        "token types": sorted(set(token_defs.tokens) - tokens_seen),
        "keywords": sorted(k for k in token_defs.reserved if k not in lexemes_seen),
        "AST node classes": sorted(set(node_classes()) - nodes_seen),
        "error call sites": [f"{pathlib.Path(f).relative_to(SRC)}:{line}"
                             for (f, line), stmt in sorted(error_lines().items())
                             if (f, line) not in hit_lines and (f, stmt) not in hit_lines],
    }
    bad = 0
    for what, items in missing.items():
        print(f"{what}: {'ALL COVERED' if not items else 'MISSING ' + str(len(items))}")
        for i in items:
            print("   ", i)
        bad += len(items)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
