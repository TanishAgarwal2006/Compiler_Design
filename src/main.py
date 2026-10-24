"""Compiler driver: C source in, three-address-code (IR) file out.

    python3 src/main.py prog.c -o prog.ir     compile to an IR file
    python3 src/main.py prog.c --tac          print the IR
    python3 src/main.py prog.c --tokens --ast --symbols --semantic   show a stage

Exit code 0 = success, 1 = the program has an error (printed to stderr, no IR written).
"""
import argparse
import os
import sys

from phase1_lexical_analysis.lexer import build_lexer
from phase2_syntax_analysis.ast_nodes import format_ast
from phase2_syntax_analysis.parser import parse_source
from common.errors import clear_errors, lex_errors, syntax_errors, semantic_errors, format_errors
from common.symbol_classifier import format_enriched_token_table, format_symbol_table
from phase3_intermediate_code.semantic_analyzer import analyze, format_semantic
from phase3_intermediate_code.ir_generator import generate, GenError
from phase3_intermediate_code.tac import format_module


def tokenize_source(code: str):
    """Return the token table for one source file."""
    lexer = build_lexer()
    lexer.lineno = 1
    lexer.input(code)

    token_rows = []
    in_typedef = False
    brace_depth = 0
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_rows.append((tok.value, tok.type))
        if tok.type == "TYPEDEF":
            in_typedef = True
        elif tok.type == "LBRACE":
            brace_depth += 1
        elif tok.type == "RBRACE":
            brace_depth -= 1
        elif in_typedef and brace_depth == 0 and tok.type == "IDENTIFIER":
            # Only the name at the end of the typedef (brace depth back to 0)
            # is the type being introduced - a member inside "typedef struct
            # { ... } P;" must stay an ordinary IDENTIFIER, not a TYPENAME.
            lexer.typedefs.add(tok.value)
        if tok.type == "SEMI" and brace_depth == 0:
            in_typedef = False

    return token_rows


def fail(filename: str, code: str) -> None:
    print(format_errors(filename, code), file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Toy C compiler front end (C subset -> three-address code)")
    ap.add_argument("source", help="C source file")
    ap.add_argument("-o", dest="ir_path", metavar="FILE.ir", help="write the IR to this file (implies --tac)")
    for flag, text in (("tokens", "print the token table"), ("ast", "print the syntax tree"),
                       ("symbols", "print the symbol report"), ("semantic", "print the scoped symbol table"),
                       ("tac", "generate IR (printed unless -o is given)"), ("all", "tokens + ast + symbols")):
        ap.add_argument("--" + flag, action="store_true", help=text)
    a = ap.parse_args()

    try:
        with open(a.source, encoding="utf-8") as f:
            code = f.read()
    except OSError as exc:
        sys.exit(f"cannot read '{a.source}': {exc.strerror}")

    run_tac = a.tac or bool(a.ir_path)
    shown = a.tokens or a.ast or a.symbols or a.semantic or a.all
    show_tokens = a.tokens or a.all or not (shown or run_tac)
    show_ast, show_symbols = a.ast or a.all, a.symbols or a.all
    run_semantic = a.semantic or run_tac

    clear_errors()
    token_rows = tokenize_source(code)
    if lex_errors:
        fail(a.source, code)
    if a.tokens and not (a.all or show_ast or show_symbols or run_semantic or run_tac):
        # Phase 1 on its own: tokens only, the parser is not run.
        print("Token table (lexical analysis):")
        print("=" * 55)
        print(f"{'Lexeme':<28}Token")
        for lexeme, ttype in token_rows:
            print(f"{str(lexeme):<28}{ttype}")
        print(f"\n{len(token_rows)} tokens, no lexical errors")
        return
    ast = parse_source(code)
    if lex_errors or syntax_errors or ast is None:
        fail(a.source, code)

    if show_tokens:
        print("Token table (lexical analysis + classification):")
        print("=" * 55)
        print(format_enriched_token_table(token_rows, ast))
    if not run_tac or shown:
        print("\nSyntax analysis: OK")

    if run_semantic:
        result = analyze(ast)
        if semantic_errors:
            fail(a.source, code)
        if not run_tac or shown:
            print("Semantic analysis: OK\n")
        if a.semantic:
            print(format_semantic(result))

    if run_tac:
        try:
            ir_text = format_module(generate(ast, result))
        except GenError as exc:
            semantic_errors.append(f"semantic error at line {exc.line}: {exc.message}")
            fail(a.source, code)
        if a.ir_path:
            os.makedirs(os.path.dirname(a.ir_path) or ".", exist_ok=True)
            with open(a.ir_path, "w", encoding="utf-8") as f:
                f.write(ir_text)
            print(f"IR written to {a.ir_path}")
        else:
            print(ir_text, end="")

    if show_symbols:
        print("\nSymbol report:")
        print(format_symbol_table(ast))
    if show_ast:
        print("\nAbstract syntax tree:")
        print(format_ast(ast))


if __name__ == "__main__":
    main()
