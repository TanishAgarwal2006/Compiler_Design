// Feature: Functions (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.


/* ---- bug: arg_type_mismatch -- argument 1 of 'f' ---- */
int arg_type_mismatch_f(int a) { return a; }
int bug_arg_type_mismatch(void) {
    int b[2];
    return arg_type_mismatch_f(b);
}

/* ---- bug: call_too_many_args -- expects 1 argument(s) but 2 were given ---- */
int call_too_many_args_f(int a) { return a; } int bug_call_too_many_args(void) { return call_too_many_args_f(1, 2); }

/* ---- bug: call_undeclared_function -- call to undeclared function 'foo' ---- */
int bug_call_undeclared_function(void) {
    foo();
    return 0;
}

/* ---- bug: missing_return_value -- should return a value ---- */
int missing_return_value_f(void) {
    return;
}
int bug_missing_return_value(void) {
    return missing_return_value_f();
}

/* ---- bug: return_type_mismatch -- cannot return a value of type char* ---- */
int return_type_mismatch_f(void) {
    return "hi";
}
int bug_return_type_mismatch(void) {
    return return_type_mismatch_f();
}

/* ---- bug: return_value_in_void -- should not return a value ---- */
void return_value_in_void_f(void) {
    return 1;
}
int bug_return_value_in_void(void) {
    return_value_in_void_f();
    return 0;
}

/* ---- bug: wrong_arg_count -- expects 1 argument(s) but 2 were given ---- */
int wrong_arg_count_f(int a) { return a; }
int bug_wrong_arg_count(void) {
    return wrong_arg_count_f(1, 2);
}

int main(void) { return 0; }
