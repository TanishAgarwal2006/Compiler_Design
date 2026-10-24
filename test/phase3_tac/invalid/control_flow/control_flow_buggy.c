// Feature: Control Flow (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.


/* ---- bug: break_outside_loop -- 'break' outside a loop or switch ---- */
int bug_break_outside_loop(void) {
    break;
    return 0;
}

/* ---- bug: case_not_constant -- case value must be a constant expression ---- */
int bug_case_not_constant(void) {
    int x = 1, y = 2;
    switch (x) {
        case y: break;
    }
    return 0;
}

/* ---- bug: continue_in_switch -- 'continue' outside a loop ---- */
int bug_continue_in_switch(void) {
    int x = 1;
    switch (x) {
        case 1: continue;
    }
    return 0;
}

/* ---- bug: continue_outside_loop -- 'continue' outside a loop ---- */
int bug_continue_outside_loop(void) {
    continue;
    return 0;
}

/* ---- bug: duplicate_case -- duplicate case value 1 ---- */
int bug_duplicate_case(void) {
    int x = 1;
    switch (x) {
        case 1: break;
        case 1: break;
    }
    return 0;
}

/* ---- bug: duplicate_default -- duplicate 'default' ---- */
int bug_duplicate_default(void) {
    int x = 1;
    switch (x) {
        default: break;
        default: break;
    }
    return 0;
}

/* ---- bug: duplicate_label -- duplicate label 'again' ---- */
int bug_duplicate_label(void) {
again:
    ;
again:
    return 0;
}

/* ---- bug: goto_undefined_label -- goto to undefined label 'nowhere' ---- */
int bug_goto_undefined_label(void) {
    goto nowhere;
    return 0;
}

/* ---- bug: label_scope_other_func -- goto to undefined label 'L' ---- */
void f(void) { goto L; } int bug_label_scope_other_func(void) { L: return 0; }

int main(void) { return 0; }
