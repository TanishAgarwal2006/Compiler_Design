"""Unit tests: arrays, row-major offsets, initialisers, data section."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_tac_basic import body, compile_ir, run_c  # noqa: E402


def test_spec_array_example():
    ir = compile_ir("int main(void) { int a[3][4]; int i = 1, j = 2; a[i][j] += 2; return 0; }")
    code = body(ir)
    assert code[2:8] == ["t1 = i * 16", "t2 = j * 4", "t3 = t1 + t2",
                         "t4 = a[t3]", "t5 = t4 + 2", "a[t3] = t5"]


def test_constant_indices_fold_into_one_offset():
    ir = compile_ir("int main(void) { int a[3][4]; a[2][1] = 5; return 0; }")
    assert "a[36] = 5" in body(ir)


def test_char_array_uses_width_one():
    ir = compile_ir("int main(void) { char s[4]; int i = 2; s[i] = 'x'; return 0; }")
    assert "s[i] = 120" in body(ir)


def test_global_array_data_line():
    ir = compile_ir("int t[4] = {1, 2, 3, 4};\nint u[3] = {5};\nint main(void) { return 0; }")
    assert "global t : int[4] = {1,2,3,4}" in ir and "global u : int[3] = {5}" in ir


def test_partial_local_initialiser_is_zero_filled():
    assert run_c('int main(void){int a[4]={1,2}; printf("%d%d%d%d", a[0],a[1],a[2],a[3]); return 0;}') == b"1200"


def test_incdec_on_element_evaluates_index_once():
    assert run_c('int main(void){int a[3]={0,0,0}; int i=0; a[i++]+=5; a[i++]++; '
                 'printf("%d%d%d %d", a[0],a[1],a[2], i); return 0;}') == b"510 2"


def test_string_literal_can_be_indexed():
    assert run_c('int main(void){printf("%c", "xyz"[2]); return 0;}') == b"z"

