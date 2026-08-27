#!/usr/bin/env python3
"""
Phase 1 - Lexical Analysis Runner
"""
import glob
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase1_lexical_analysis.lexer import build_lexer
from common.errors import clear_errors, lex_errors
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


def format_token_table(token_rows) -> str:
    lines = [f"{'Token':<25} {'Token_Type':<20}", "-" * 45]
    for lexeme, token_name in token_rows:
        lines.append(f"{str(lexeme):<25} {token_name:<20}")
    return "\n".join(lines)


def run_batch_lexical(test_pattern: str, title: str, output_file: str = None):
    repo_root = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
    search_path = os.path.join(repo_root, test_pattern)
    files = sorted(glob.glob(search_path)) or sorted(glob.glob(test_pattern))

    output_buffer = ["=" * 60, f" {title}", "=" * 60]
    passed_count = 0
    total_count = len(files)

    for filepath in files:
        rel_path = os.path.relpath(filepath, repo_root) if os.path.isabs(filepath) else filepath
        output_buffer.extend(["\n----------------------------------------", f"Lexical Analysis for: {rel_path}", "----------------------------------------"])

        code = read_source(filepath)
        clear_errors()
        token_rows = tokenize_source(code)

        if lex_errors:
            output_buffer.append("[FAIL / Lexical Errors Detected]")
            err_msg = "\n".join(lex_errors)
            for err in lex_errors:
                output_buffer.append(f"  {err}")
            write_case_logs(filepath, errors_str=err_msg)
        else:
            passed_count += 1
            output_buffer.append("[PASS / Valid Tokenization]")
            tok_table = format_token_table(token_rows)
            output_buffer.append(tok_table)
            write_case_logs(filepath, tokens_str=tok_table)

    output_buffer.extend(["\n" + "=" * 60, f" Batch Result: {passed_count}/{total_count} files tokenized successfully", "=" * 60])
    full_output = "\n".join(output_buffer)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_output + "\n")
        print(f"Batch lexical analysis complete. Result written to '{output_file}'.")
    else:
        print(full_output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_lexer.py <source_file|--phase1|--all> [--output <file>]")
        sys.exit(1)

    arg1 = sys.argv[1]
    output_file = None

    args = sys.argv[2:]
    for i in range(len(args)):
        if args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]

    if arg1 == "--phase1":
        run_batch_lexical("tests/phase1_lexical/*/*.c", "Phase 1 Lexical Analysis (Phase 1 Test Suite)", output_file)
        return
    elif arg1 == "--all":
        run_batch_lexical("tests/*/*/*.c", "Phase 1 Lexical Analysis (All Test Cases)", output_file)
        return

    filename = arg1
    code = read_source(filename)
    clear_errors()
    token_rows = tokenize_source(code)

    if lex_errors:
        err_msg = "\n".join(lex_errors)
        write_case_logs(filename, errors_str=err_msg)
        print("--- Lexical Errors Detected ---")
        for err in lex_errors:
            print(err)
        sys.exit(1)

    formatted_table = format_token_table(token_rows)
    log_file = write_case_logs(filename, tokens_str=formatted_table)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Lexical Analysis Output for: {filename}\n{'=' * 50}\n\n{formatted_table}\n")
        print(f"Tokenization successful. Output written to '{output_file}' and log saved to '{log_file}'.")
    else:
        print(f"Lexical Analysis Output:\n{'=' * 50}\n{formatted_table}\n\n(Log saved to '{log_file}')")


if __name__ == "__main__":
    main()
