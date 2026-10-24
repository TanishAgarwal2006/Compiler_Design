// Feature: Types (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.


/* ---- bug: assign_to_array -- cannot assign to an array ---- */
int bug_assign_to_array(void) {
    int a[3];
    int b[3];
    a = b;
    return 0;
}

/* ---- bug: assign_to_const -- read-only variable 'k' ---- */
int bug_assign_to_const(void) {
    const int k = 1;
    k = 2;
    return 0;
}

/* ---- bug: assign_to_literal -- cannot assign to this expression ---- */
int bug_assign_to_literal(void) { 5 = 3; return 0; }

/* ---- bug: bool_array_assign -- assign to a bool array ---- */
int bug_bool_array_assign(void) {
    bool b[2];
    b = 1;
    return 0;
}

/* ---- bug: bool_string_init -- bool from a string ---- */
int bug_bool_string_init(void) {
    bool b = "hi";
    return b;
}

/* ---- bug: char_string_assign -- cannot initialize 'c' of type char ---- */
int bug_char_string_assign(void) { char c = "abc"; return 0; }

/* ---- bug: condition_not_scalar -- condition of 'if' must be ---- */
int bug_condition_not_scalar(void) {
    int a[3];
    if (a) return 1;
    return 0;
}

/* ---- bug: division_by_zero -- division by zero ---- */
int bug_division_by_zero(void) {
    int x = 1 / 0;
    return x;
}

/* ---- bug: float_bitwise -- operator '&' needs int or char operands ---- */
int bug_float_bitwise(void) { float f = 1.0f; int x = f & 1; return x; }

/* ---- bug: incr_non_lvalue -- cannot apply '++' ---- */
int bug_incr_non_lvalue(void) { int a = 1; (a + 1)++; return 0; }

/* ---- bug: modulo_float -- operator '%' needs int or char operands ---- */
int bug_modulo_float(void) {
    float f = 1.0;
    float g = f % 2;
    return 0;
}

/* ---- bug: switch_float -- switch expression must be an int or char ---- */
int bug_switch_float(void) {
    float f = 1.0;
    switch (f) {
        case 1: break;
    }
    return 0;
}

/* ---- bug: use_void_arg -- cannot pass void where int is expected ---- */
void g(void) {} int use_void_arg_f(int a) { return a; } int bug_use_void_arg(void) { return use_void_arg_f(g()); }

/* ---- bug: void_in_expression -- with a value of type void ---- */
void void_in_expression_f(void) { }
int bug_void_in_expression(void) {
    int x = void_in_expression_f();
    return x;
}

int main(void) { return 0; }
