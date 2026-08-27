#!/usr/bin/env python3
"""
Phase 2 - Syntax Analysis Runner

Performs syntax analysis on a C source file, builds the Abstract Syntax Tree (AST),
and generates a Detailed Symbol Table.

Usage:
    python run_parser.py <source.c> [--ast-file <file>] [--symbol-file <file>] [--output <file>]
    python src/phase2_syntax_analysis/run_parser.py <source.c>
"""
import os
import sys

# Ensure parent 'src' directory is in sys.path so imports work regardless of CWD
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase2_syntax_analysis.ast_nodes import format_ast
from phase2_syntax_analysis.parser import parse_source
from common.errors import clear_errors, lex_errors, syntax_errors
from common.symbol_classifier import format_symbol_table, classify_program_detailed
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


import glob


def run_batch_syntax(test_pattern: str, title: str, output_file: str = None):
    repo_root = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
    search_path = os.path.join(repo_root, test_pattern)
    files = sorted(glob.glob(search_path))

    if not files:
        files = sorted(glob.glob(test_pattern))

    output_buffer = []
    output_buffer.append("=" * 60)
    output_buffer.append(f" {title}")
    output_buffer.append("=" * 60)

    passed_count = 0
    total_count = len(files)

    for filepath in files:
        rel_path = os.path.relpath(filepath, repo_root) if os.path.isabs(filepath) else filepath
        output_buffer.append(f"\n----------------------------------------")
        output_buffer.append(f"Syntax Analysis for: {rel_path}")
        output_buffer.append(f"----------------------------------------")

        code = read_source(filepath)
        clear_errors()
        ast = parse_source(code)

        if lex_errors or syntax_errors or ast is None:
            output_buffer.append("[FAIL / Syntax or Lexical Errors Detected]")
            err_lines = []
            if lex_errors:
                for err in lex_errors:
                    output_buffer.append(f"  Lex error: {err}")
                    err_lines.append(f"Lex error: {err}")
            if syntax_errors:
                for err in syntax_errors:
                    output_buffer.append(f"  Syntax error: {err}")
                    err_lines.append(f"Syntax error: {err}")
            write_case_logs(filepath, errors_str="\n".join(err_lines))
        else:
            passed_count += 1
            output_buffer.append("[PASS / Syntax Analysis Successful]")
            sym_table_str = format_symbol_table(ast)
            ast_nodes_str = format_ast(ast)
            output_buffer.append("\nDetailed Symbol Table:")
            output_buffer.append(sym_table_str)
            output_buffer.append("\nAST:")
            output_buffer.append(ast_nodes_str)
            write_case_logs(filepath, symbols_str=sym_table_str, ast_str=ast_nodes_str)

    output_buffer.append("\n" + "=" * 60)
    output_buffer.append(f" Batch Result: {passed_count}/{total_count} files parsed successfully")
    output_buffer.append("=" * 60)

    full_output = "\n".join(output_buffer)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_output + "\n")
        print(f"Batch syntax analysis complete. Result written to '{output_file}' and logs saved under 'logs/'.")
    else:
        print(full_output)
        print(f"\n(Individual per-case log files saved under 'logs/')")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python run_parser.py <source_file> [--output <file>]")
        print("  Phase 2 files only: python run_parser.py --phase2 [--output <file>]")
        print("  All project files:  python run_parser.py --all [--output <file>]")
        sys.exit(1)

    arg1 = sys.argv[1]
    ast_file = None
    symbol_file = None
    output_file = None

    args = sys.argv[2:]
    for i in range(len(args)):
        if args[i] == "--ast-file" and i + 1 < len(args):
            ast_file = args[i + 1]
        elif args[i] == "--symbol-file" and i + 1 < len(args):
            symbol_file = args[i + 1]
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]

    if arg1 == "--phase2":
        pattern = "tests/phase2_syntax/*/*.c"
        run_batch_syntax(pattern, "Phase 2 Syntax Analysis (Phase 2 Test Suite)", output_file)
        return
    elif arg1 == "--all":
        pattern = "tests/*/*/*.c"
        run_batch_syntax(pattern, "Phase 2 Syntax Analysis (All Test Cases)", output_file)
        return

    filename = arg1
    code = read_source(filename)
    clear_errors()

    ast = parse_source(code)

    if lex_errors or syntax_errors or ast is None:
        err_lines = []
        if lex_errors:
            print("--- Lexical Errors Detected ---")
            for err in lex_errors:
                print(err)
                err_lines.append(f"Lex error: {err}")
        if syntax_errors:
            print("--- Syntax Errors Detected ---")
            for err in syntax_errors:
                print(err)
                err_lines.append(f"Syntax error: {err}")
        write_case_logs(filename, errors_str="\n".join(err_lines))
        sys.exit(1)

    ast_str = format_ast(ast)
    symbol_table_str = format_symbol_table(ast)
    log_file = write_case_logs(filename, symbols_str=symbol_table_str, ast_str=ast_str)

    if ast_file:
        with open(ast_file, "w", encoding="utf-8") as f:
            f.write(f"Abstract Syntax Tree (AST) for: {filename}\n")
            f.write("=" * 60 + "\n\n")
            f.write(ast_str + "\n")
        print(f"AST written to '{ast_file}'.")

    if symbol_file:
        with open(symbol_file, "w", encoding="utf-8") as f:
            f.write(f"Detailed Symbol Table for: {filename}\n")
            f.write("=" * 60 + "\n\n")
            f.write(symbol_table_str + "\n")
        print(f"Symbol table written to '{symbol_file}'.")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Syntax Analysis Output for: {filename}\n")
            f.write("=" * 60 + "\n\n")
            f.write("Status: Syntax analysis successful.\n\n")
            f.write("Detailed Symbol Table:\n")
            f.write("-" * 35 + "\n")
            f.write(symbol_table_str + "\n")
        print(f"Full syntax analysis output written to '{output_file}'.")

    if not (symbol_file or output_file):
        print("Syntax analysis successful.\n")
        print("Detailed Symbol Table:")
        print("=" * 84)
        print(symbol_table_str)
        print(f"\n(Log saved to '{log_file}')")





if __name__ == "__main__":
    main()

