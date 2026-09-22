// Covers: line and block comments, preprocessor directives, and float literals
#include <stdio.h>
#define MAX 100

/* a block
   comment spanning
   multiple lines */
int main() { // trailing comment
    int x = 5; /* inline block comment */
    float a = 3.14;
    double b = 2.5e-3;
    float c = .5f;
    double d = 1e10;
    return 0;
}
