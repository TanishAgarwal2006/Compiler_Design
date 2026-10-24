// Feature: Declarations (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.
#include <stdio.h>

/* ---- bug: conflicting_prototype -- conflicting types for 'f' ---- */
int conflicting_prototype_f(int a);
float conflicting_prototype_f(int a);
int bug_conflicting_prototype(void) { return 0; }

/* ---- bug: enum_dup -- redeclaration of 'A' ---- */
enum E { A, B, A }; int bug_enum_dup(void) { return 0; }

/* ---- bug: extern_never_defined -- extern without a definition ---- */
extern int x;
int bug_extern_never_defined(void) { return x; }

/* ---- bug: global_nonconst_init -- not a constant expression ---- */
int h(void) { return 1; } int g = h(); int bug_global_nonconst_init(void) { return 0; }

/* ---- bug: multiple_errors -- three different mistakes, all reported (one fragment per line in the .err file) ---- */
int bug_multiple_errors(void) {
    int a = 1;
    int a = 2;
    b = 3;
    printf("%d\n", undefined_name);
    return 0;
}

/* ---- bug: redecl_param -- redeclaration of 'a' ---- */
int redecl_param_f(int a) { int a = 2; return a; } int bug_redecl_param(void) { return redecl_param_f(1); }

/* ---- bug: redeclaration -- redeclaration of 'a' ---- */
int bug_redeclaration(void) {
    int a = 1;
    int a = 2;
    return a;
}

/* ---- bug: redefinition_function -- redefinition of function 'f' ---- */
int redefinition_function_f(void) { return 1; }
int redefinition_function_f(void) { return 2; }
int bug_redefinition_function(void) { return redefinition_function_f(); }

/* ---- bug: reserved_name -- 'atoi' is a reserved name ---- */
int atoi(int a) {
    return a;
}
int bug_reserved_name(void) {
    return 0;
}

/* ---- bug: undeclared_identifier -- use of undeclared identifier 'y' ---- */
int bug_undeclared_identifier(void) {
    return y;
}

/* ---- bug: undeclared_out_of_scope -- use of undeclared identifier 'a' ---- */
int bug_undeclared_out_of_scope(void) {
    {
        int a = 1;
    }
    return a;
}

/* ---- bug: void_variable -- variable 'v' declared void ---- */
int bug_void_variable(void) {
    void v;
    return 0;
}

int main(void) { return 0; }
