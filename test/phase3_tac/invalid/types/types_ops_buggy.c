// Feature: Types in operators (deliberately wrong)
// Every function holds one mistake; the .err file lists the message each one must produce.

void nothing(void) { }
int target(void) { return 0; }

int bug_function_as_value(void) { int x = target; return x; }
int bug_string_to_int(void) { int x; x = "s"; return x; }
int bug_compound_on_string(void) { char *s = "a"; s += 1; return 0; }
int bug_mod_assign_float(void) { float f = 1.0; f %= 2; return 0; }
int bug_not_on_float(void) { float f = 1.0; int x = ~f; return x; }
int bug_negate_string(void) { char *s = "a"; int x = -s; return x; }
int bug_increment_string(void) { char *s = "a"; s++; return 0; }
int bug_sizeof_void(void) { int x = sizeof(void); return x; }
int bug_ternary_branches(void) { int x = 1 ? "a" : 2; return x; }
int bug_cast_to_void(void) { int x = (void)1; return x; }
int bug_void_in_binary(void) { int x = 1 + nothing(); return x; }
int bug_void_in_unary(void) { int x = -nothing(); return x; }
int bug_divide_assign_by_zero(void) { int x = 5; x /= 0; return x; }

int main(void) { return 0; }
