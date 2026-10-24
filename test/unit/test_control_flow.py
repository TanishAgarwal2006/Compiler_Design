"""Unit tests: control flow lowering (labels, short-circuit, switch)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_tac_basic import body, compile_ir, run_c  # noqa: E402


def test_short_circuit_spec_example():
    ir = compile_ir("int main(void) { int a=1,b=2,c=3,x=0; if (a < b && c) x = 1; return 0; }")
    assert body(ir)[4:12] == ["if a < b goto L3", "goto L2", "L3:", "if c != 0 goto L1",
                              "goto L2", "L1:", "x = 1", "L2:"]


def test_and_or_do_not_evaluate_rhs_when_decided():
    assert run_c('int main(void){int a=0; 0 && (a=1); 1 || (a=2); '
                 'printf("%d", a); return 0;}') == b"0"


def test_continue_in_for_runs_update():
    assert run_c('int main(void){int i,n=0; for(i=0;i<5;i++){if(i%2)continue;n++;} '
                 'printf("%d %d", i, n); return 0;}') == b"5 3"


def test_continue_inside_switch_targets_loop():
    assert run_c('int main(void){int i; for(i=0;i<3;i++){switch(i){case 1: continue;} '
                 'printf("%d", i);} return 0;}') == b"02"


def test_switch_default_in_middle_falls_through():
    assert run_c('int main(void){switch(9){case 1: printf("a"); default: printf("d"); '
                 'case 2: printf("b");} return 0;}') == b"db"


def test_goto_label_is_function_scoped_name():
    ir = compile_ir("int main(void) { goto end; end: return 0; }")
    assert "goto L_main_end" in body(ir) and "L_main_end:" in body(ir)


def test_until_and_do_until():
    assert run_c('int main(void){int i=0; until(i==3) i++; do i--; until(i<=1); '
                 'printf("%d", i); return 0;}') == b"1"
