"""Unit tests: the wording of the three syntax-error messages and the recovery after an error."""
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.errors import clear_errors, syntax_errors  # noqa: E402
from phase2_syntax_analysis.parser import parse_source  # noqa: E402


def errors_of(src):
    clear_errors()
    parse_source(src)
    return list(syntax_errors)


def test_end_of_file_message():
    (msg,) = errors_of("int main(void) { int x = 1")
    assert "unexpected end of file" in msg and "'}' or ';'" in msg and msg.endswith("at line 1")


def test_missing_semicolon_hint_points_at_the_previous_line():
    (msg,) = errors_of("int main(void) {\n    int x = 1\n    return x;\n}\n")
    assert "unexpected token 'return'" in msg and "is a ';' missing at the end of line 2?" in msg
    assert msg.endswith("at line 3")


def test_plain_unexpected_token_has_no_hint():
    (msg,) = errors_of("int main(void) { int x = ); return 0; }\n")
    assert "unexpected token ')'" in msg and "missing" not in msg


def test_parser_recovers_and_reports_each_bad_statement_once():
    msgs = errors_of("int main(void) {\n int a = ;\n int b = 2;\n int c = ;\n return 0;\n}\n")
    assert len(msgs) == 2 and msgs[0].endswith("at line 2") and msgs[1].endswith("at line 4")
