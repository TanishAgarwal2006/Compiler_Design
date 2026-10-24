/* Syntax analysis: declarations, types and qualifiers
   (several small programs joined into one file; each part is marked by a comment line) */

/* ---------- part: declarations_and_blocks.c ---------- */
// Covers: multiple declarators sharing one type_specifier, empty statements,
// and nested compound blocks
typedef int integer;
typedef char character;

int main() {
    integer a, b = 5, arr1D[10], arr2D[5][5];
    character str[20], ch = 'A';

    integer counter = 0;
    do {
        arr1D[counter] = counter * 2;
        counter++;
    } while (counter < 10);

    ;
    ;
    {
        {
            int nested = 1;
        }
    }

    return 0;
}

/* ---------- part: types_and_qualifiers.c ---------- */
// Covers: float/double, integer size/sign modifiers, const, static/extern,
// and bool
#include <stdio.h>

extern int shared_counter;
static int local_counter = 0;

double average(int a, int b) {
    double total = a + b;
    return total / 2.0;
}

int main() {
    float f = 3.14;
    double d = 2.5e-3;
    unsigned long int big = 4000000;
    const short s = 12;
    signed char c = 'a';
    const int limit = 10;
    bool flag = true;
    flag = false;

    d = average(4, 6);
    local_counter = limit;
    printf("%f %f\n", f, d);
    return local_counter;
}

/* ---------- part: test1_variables_vs_procedures.c ---------- */


int a(int b, int c) {
    return b + c;
}

int main() {
    int a;
    a = 5;
    int result = a + 1;
    return 0;
}
