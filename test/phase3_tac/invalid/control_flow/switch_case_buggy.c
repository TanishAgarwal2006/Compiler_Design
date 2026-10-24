// Feature: switch - a case label that is not an integer constant
int bug_case_float(int x) { switch (x) { case 1.5: break; } return 0; }
int main(void) { return 0; }
