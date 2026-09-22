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
