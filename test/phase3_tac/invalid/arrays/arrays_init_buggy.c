// Feature: Arrays - initializer and declaration mistakes (deliberately wrong)
// Every function holds one mistake; the .err file lists the message each one must produce.

int bug_missing_inner_size(void) { int a[3][]; return 0; }
int bug_void_array(void) { void a[3]; return 0; }
int bug_scalar_init_for_array(void) { int a[3] = 5; return 0; }
int bug_string_for_int_array(void) { int a[3] = "xy"; return 0; }
int bug_mixed_nested_flat(void) { int a[2][2] = {{1}, 2}; return 0; }
int bug_braces_in_1d(void) { int a[3] = {{1}, {2}}; return 0; }
int bug_too_many_rows(void) { int a[2][2] = {{1}, {2}, {3}}; return 0; }
int bug_too_many_rows_3d(void) { int a[2][2][2] = {{{1}}, {{2}}, {{3}}}; return 0; }
int bug_too_many_in_inner_level(void) { int a[2][2][2] = {{{1}, {2}, {3}}}; return 0; }
int bug_braces_too_deep(void) { int a[2][2] = {{{1}}}; return 0; }
int bug_mixed_nested_flat_3d(void) { int a[2][2][2] = {{{1}, 2}}; return 0; }
int bug_element_type(void) { int a[2] = {"x", 1}; return 0; }

int gv = 1;
int bug_global_not_constant[2] = {1, gv};
char *bug_global_string_from_int = gv;
char *other = "q";
char *bug_global_string_from_variable = other;

int main(void) { return 0; }
