// Feature: Declarations and parameters (deliberately wrong)
// Every part holds one mistake; the .err file lists the message each one must produce.

enum Color { RED, GREEN };
int bug_unknown_enum(void) { enum Nope v; return 0; }
int bug_scalar_in_braces(void) { int x = {1}; return x; }

int bug_name_clash;
int bug_name_clash(void);

int bug_void_param(void x) { return 0; }
int bug_unnamed_param(int) { return 0; }
int bug_duplicate_param(int a, int a) { return a; }

typedef int Row[3];
Row bug_function_returns_array(void) { Row r; return r; }

int taken;
typedef int taken;

int main(void) { return 0; }
