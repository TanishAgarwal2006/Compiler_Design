"""
Per-test-case log file generator.
Generates single log files under: logs/<phase>/<category>/<file_name>.log
"""
import os
from typing import Optional


def get_log_file_path(source_path: str, base_log_dir: str = "logs") -> str:
    norm = os.path.normpath(source_path)
    parts = norm.split(os.sep)
    file_basename = os.path.splitext(os.path.basename(norm))[0]

    if "tests" in parts:
        idx = parts.index("tests")
        sub_parts = parts[idx + 1 :-1]
        log_dir = os.path.join(base_log_dir, *sub_parts)
    else:
        log_dir = os.path.join(base_log_dir, "custom")

    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"{file_basename}.log")


def write_case_logs(
    source_path: str,
    tokens_str: Optional[str] = None,
    symbols_str: Optional[str] = None,
    ast_str: Optional[str] = None,
    errors_str: Optional[str] = None,
    base_log_dir: str = "logs",
) -> str:
    log_file = get_log_file_path(source_path, base_log_dir)

    lines = [
        "=" * 70,
        f" Compiler Analysis Report for: {source_path}",
        "=" * 70,
    ]

    if errors_str:
        lines.extend(["\nSTATUS: [ERRORS DETECTED]", "-" * 35, errors_str])
    else:
        lines.append("\nSTATUS: [SUCCESS / PASSED]")

    if tokens_str:
        lines.extend(["\n" + "=" * 70, " Phase 1: Tokenization Output", "=" * 70, tokens_str])

    if symbols_str:
        lines.extend(["\n" + "=" * 70, " Phase 2: Detailed Symbol Table", "=" * 70, symbols_str])

    if ast_str:
        lines.extend(["\n" + "=" * 70, " Phase 2: Abstract Syntax Tree (AST)", "=" * 70, ast_str])

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return log_file
