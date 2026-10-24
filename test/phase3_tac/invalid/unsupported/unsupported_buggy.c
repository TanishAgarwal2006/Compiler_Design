// Feature: Unsupported (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.
#include <stdio.h>
#include <stdlib.h>

/* ---- bug: auto_type -- 'auto' type deduction ---- */
int bug_auto_type(void) {
    auto x = 5;
    return x;
}

/* ---- bug: class_method_outside -- Class::method definition outside the class ---- */
class class_method_outside_A {
public:
    int class_method_outside_f();
};
int class_method_outside_A::class_method_outside_f() { return 1; }
int bug_class_method_outside(void) { return 0; }

/* ---- bug: class_object -- class X x; ---- */
class X {
public:
    int a;
};
int bug_class_object(void) {
    class X x;
    return 0;
}

/* ---- bug: constructor -- constructors ---- */
class constructor_A {
public:
    int x;
    constructor_A() { x = 1; }
};
int bug_constructor(void) { return 0; }

/* ---- bug: delete_expression -- delete[] ---- */
int bug_delete_expression(void) {
    int a[2];
    delete[] a;
    return 0;
}

/* ---- bug: destructor -- destructors ---- */
class destructor_A {
public:
    int x;
    ~destructor_A() { }
};
int bug_destructor(void) { return 0; }

/* ---- bug: fclose_call -- fclose ---- */
int bug_fclose_call(void) {
    fclose(0);
    return 0;
}

/* ---- bug: fopen_call -- fopen and the FILE type ---- */
int bug_fopen_call(void) {
    FILE *f = fopen("a", "r");
    return 0;
}

/* ---- bug: free_call -- free ---- */
int bug_free_call(void) {
    free(0);
    return 0;
}

/* ---- bug: lambda_expression -- lambda functions (and the auto that holds it) ---- */
int bug_lambda_expression(void) {
    auto f = [](int a) -> int { return a; };
    return 0;
}

/* ---- bug: lambda_immediate_call -- a lambda called at once is not a direct call ---- */
int bug_lambda_immediate_call(void) {
    int k = 1;
    int r = [k](int a) -> int { return a + k; }(2);
    return r;
}

/* ---- bug: malloc_call -- malloc ---- */
int bug_malloc_call(void) {
    int a = malloc(4);
    return 0;
}

/* ---- bug: new_expression -- new ---- */
int bug_new_expression(void) {
    int *p = new int;
    return 0;
}

/* ---- bug: reference_param -- references ---- */
int reference_param_f(int &a) { return a; }
int bug_reference_param(void) {
    int x = 1;
    return reference_param_f(x);
}

/* ---- bug: reference_return -- reference parameter and reference return type ---- */
int &reference_return_f(int &a) { return a; }
int bug_reference_return(void) { return 0; }

/* ---- bug: reference_variable -- references ---- */
int bug_reference_variable(void) {
    int x = 1;
    int &r = x;
    return r;
}

/* ---- bug: scope_without_class -- Class::method of a class that was never declared ---- */
int Dog::bark() { return 1; }
int bug_scope_without_class(void) { return 0; }

/* ---- bug: this_keyword -- this ---- */
int bug_this_keyword(void) {
    return this;
}

/* ---- bug: unsupported_address_of -- address-of '&' is only supported inside scanf arguments ---- */
int bug_unsupported_address_of(void) {
    int x = 1;
    int y = &x;
    return y;
}

/* ---- bug: unsupported_class -- unsupported feature: classes ---- */
class unsupported_class_A {
public:
    int x;
};
int bug_unsupported_class(void) {
    return 0;
}

/* ---- bug: unsupported_deref -- unsupported feature: pointer dereference '*' ---- */
int bug_unsupported_deref(void) {
    int x = 1;
    return *x;
}

/* ---- bug: unsupported_pointer_var -- unsupported feature: pointers (only 'char *' strings and 'argv' are accepted) ---- */
int bug_unsupported_pointer_var(void) {
    int *p;
    return 0;
}

/* ---- bug: unsupported_static_local -- unsupported feature: static local variables ---- */
int bug_unsupported_static_local(void) {
    static int n = 0;
    return n;
}

/* ---- bug: unsupported_struct -- unsupported feature: struct and union ---- */
struct P {
    int x;
};
int bug_unsupported_struct(void) {
    return 0;
}

/* ---- bug: unsupported_variadic -- unsupported feature: variadic functions ---- */
int unsupported_variadic_f(int a, ...) {
    return a;
}
int bug_unsupported_variadic(void) {
    return 0;
}

int main(void) { return 0; }
