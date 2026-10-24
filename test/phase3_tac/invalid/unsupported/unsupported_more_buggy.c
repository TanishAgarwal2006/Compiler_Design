// Feature: unsupported constructs found inside function bodies (deliberately wrong)
int bug_class_in_function(void) { class Q { public: int z; }; return 0; }
int bug_lambda(void) { auto f = [](int a) { return a; }; return 0; }
int bug_new(void) { new int; return 0; }
int bug_struct_in_function(void) { struct S { int a; }; return 0; }
int bug_pointer_cast(void) { float f = 1.0; int *p = (int*)f; return 0; }
int main(void) { return 0; }
