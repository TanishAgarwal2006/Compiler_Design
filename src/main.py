"""
Compiler driver.

Usage:
    python src/main.py <source.c> [--tokens] [--ast] [--symbols] [--all]

Flags (any combination; with none given, tokens + a success/failure summary
are shown - the same default behaviour as before):
    --tokens   print the Phase 1 token table
    --ast      print the Phase 2 AST
    --symbols  print the identifier -> role table described in
               docs/identifier_classification.md (this is what tells you
               whether `fib` is a function, a variable, an array, ...)
    --all      shorthand for --tokens --ast --symbols

Currently implemented: Phase 1 (lexical analysis) and Phase 2 (syntax
analysis). Phase 3 (intermediate code generation) and Phase 4
(optimization + MIPS code generation) are scaffolded under src/ but not
yet implemented - see their README files.
"""
import os
import sys


from phase1_lexical_analysis.lexer import build_lexer
from phase2_syntax_analysis.ast_nodes import format_ast
from phase2_syntax_analysis.parser import parse_source
from common.errors import clear_errors, lex_errors, syntax_errors
from common.symbol_classifier import classify_program, format_symbol_table, format_enriched_token_table
from common.logger import write_case_logs



def read_source(filename: str) -> str:

    try:
        with open(filename, "r", encoding="utf-8") as source_file:
            return source_file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading file '{filename}': {exc}")
        sys.exit(1)


def tokenize_source(code: str):
    """Runs the lexer stand-alone (Phase 1 only) and returns (lexeme, type) pairs.

    Uses a fresh lexer instance (see build_lexer()) so this never
    interferes with, or is interfered by, any other tokenization/parsing
    happening in the same process. It mirrors the parser's own dynamic
    typedef-tracking mechanism (lexer.typedefs) so the token table always
    matches what Phase 2 actually consumes.
    """
    lexer = build_lexer()
    lexer.lineno = 1
    lexer.input(code)

    token_rows = []
    in_typedef = False
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_rows.append((tok.value, tok.type))
        if tok.type == "TYPEDEF":
            in_typedef = True
        elif in_typedef and tok.type == "IDENTIFIER":
            lexer.typedefs.add(tok.value)
        if tok.type == "SEMI":
            in_typedef = False

    return token_rows


def print_tokens(token_rows) -> None:
    print(f"{'Token':<25} {'Token_Type':<20}")
    print("-" * 45)
    for lexeme, token_name in token_rows:
        print(f"{str(lexeme):<25} {token_name:<20}")


def print_symbol_table(roles: dict) -> None:
    if not roles:
        print("(no identifiers declared)")
        return
    print(f"{'Identifier':<20} {'Role':<12}")
    print("-" * 32)
    for name, role in sorted(roles.items()):
        print(f"{name:<20} {role:<12}")


def print_errors() -> None:
    if lex_errors:
        print("--- Lexical Errors Detected ---")
        for err in lex_errors:
            print(err)
    if syntax_errors:
        print("--- Syntax Errors Detected ---")
        for err in syntax_errors:
            print(err)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <source_file> [--tokens] [--ast] [--symbols] [--all] [--ast-file <file>]")
        sys.exit(1)

    filename = sys.argv[1]
    raw_args = sys.argv[2:]
    flags = set()
    ast_file_path = None

    idx = 0
    while idx < len(raw_args):
        arg = raw_args[idx]
        if arg == "--ast-file" and idx + 1 < len(raw_args):
            ast_file_path = raw_args[idx + 1]
            flags.add("--ast")
            idx += 2
        else:
            flags.add(arg)
            idx += 1

    if "--all" in flags:
        flags.update({"--tokens", "--ast", "--symbols"})

    # Preserve default: with no flags at all, still show tokens.
    show_tokens = "--tokens" in flags or not flags
    show_ast = "--ast" in flags
    show_symbols = "--symbols" in flags

    code = read_source(filename)
    clear_errors()

    token_rows = tokenize_source(code)
    if lex_errors:
        err_msg = "\n".join(lex_errors)
        write_case_logs(filename, errors_str=err_msg)
        print_errors()
        sys.exit(1)

    ast = parse_source(code)
    if lex_errors or syntax_errors or ast is None:
        err_lines = []
        if lex_errors:
            err_lines.extend([f"Lex error: {e}" for e in lex_errors])
        if syntax_errors:
            err_lines.extend([f"Syntax error: {e}" for e in syntax_errors])
        write_case_logs(filename, errors_str="\n".join(err_lines))
        print_errors()
        sys.exit(1)

    enriched_tokens_str = format_enriched_token_table(token_rows, ast)
    symbol_table_str = format_symbol_table(ast)
    ast_nodes_str = format_ast(ast)

    log_file = write_case_logs(
        filename,
        tokens_str=enriched_tokens_str,
        symbols_str=symbol_table_str,
        ast_str=ast_nodes_str,
    )

    if show_tokens:
        print("Enriched Token Table (Phase 1 Lexical Analysis + Phase 2 Classification):")
        print("=" * 55)
        print(enriched_tokens_str)
        print()

    print("Syntax analysis successful.")

    if show_symbols:
        print()
        print("Detailed Symbol Table:")
        print(symbol_table_str)

    if show_ast and ast_file_path:
        with open(ast_file_path, "a", encoding="utf-8") as ast_f:
            ast_f.write(f"----------------------------------------\n")
            ast_f.write(f"AST for: {filename}\n")
            ast_f.write(f"----------------------------------------\n")
            ast_f.write(ast_nodes_str + "\n\n")

    print(f"\n(Analysis report logged to '{log_file}')")






if __name__ == "__main__":
    main()

