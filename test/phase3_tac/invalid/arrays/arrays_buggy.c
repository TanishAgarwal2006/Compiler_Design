// Feature: Arrays (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.


/* ---- bug: array_param_wrong_dim -- cannot pass int[2][4] where int[][3] ---- */
int array_param_wrong_dim_f(int a[][3]) { return a[0][0]; } int bug_array_param_wrong_dim(void) { int m[2][4]; return array_param_wrong_dim_f(m); }

/* ---- bug: array_size_missing -- array size missing in declaration of 'a' ---- */
int bug_array_size_missing(void) {
    int a[];
    return 0;
}

/* ---- bug: array_to_scalar_param -- cannot pass int[3] where int is expected ---- */
int array_to_scalar_param_f(int a) { return a; } int bug_array_to_scalar_param(void) { int m[3]; return array_to_scalar_param_f(m); }

/* ---- bug: index_not_integer -- array index must be an int or char ---- */
int bug_index_not_integer(void) {
    int a[3];
    float f = 1.0;
    return a[f];
}

/* ---- bug: init_array_by_scalar -- needs a brace-enclosed initializer ---- */
int bug_init_array_by_scalar(void) { int a[3] = 5; return 0; }

/* ---- bug: nonconstant_array_size -- array size of 'a' must be a constant expression ---- */
int bug_nonconstant_array_size(void) {
    int n = 3;
    int a[n];
    return 0;
}

/* ---- bug: nonpositive_array_size -- must be a positive integer ---- */
int bug_nonpositive_array_size(void) {
    int a[0];
    return 0;
}

/* ---- bug: scalar_to_array_param -- cannot pass int where int[] is expected ---- */
int scalar_to_array_param_f(int a[]) { return a[0]; } int bug_scalar_to_array_param(void) { int x = 3; return scalar_to_array_param_f(x); }

/* ---- bug: string_too_long -- string initializer is too long ---- */
int bug_string_too_long(void) {
    char s[2] = "abc";
    return 0;
}

/* ---- bug: subscript_non_array -- subscripted value is not an array ---- */
int bug_subscript_non_array(void) {
    int x = 1;
    return x[0];
}

/* ---- bug: too_many_initializers -- too many initializers for 'a' ---- */
int bug_too_many_initializers(void) {
    int a[2] = {1, 2, 3};
    return 0;
}

/* ---- bug: too_many_subscripts -- subscripted value is not an array ---- */
int bug_too_many_subscripts(void) { int a[3]; int x = a[0][1]; return x; }

int main(void) { return 0; }
