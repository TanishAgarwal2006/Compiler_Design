// Covers: bitwise operators and their compound-assignment forms, the
// ternary operator, until/do-until loops, and variadic parameters.
#include <stdarg.h>

int sum_all(int count, ...) {
    int total = 0;
    va_list args;
    int i = 0;
    while (i < count) {
        total += i;
        i++;
    }
    return total;
}

int main() {
    int a = 0b1010, b = 0b0110, r;

    r = a & b;
    r = a | b;
    r = a ^ b;
    r = ~a;
    r = a << 2;
    r = a >> 1;

    r &= b;
    r |= b;
    r ^= b;
    r <<= 1;
    r >>= 1;

    // ternary operator, including nesting
    int max = (a > b) ? a : b;
    int sign = (a > 0) ? 1 : (a < 0) ? -1 : 0;

    // until: repeats while the condition is false
    int n = 0;
    until (n >= 5) {
        n++;
    }

    // do-until: same, but checks after the first iteration
    int m = 0;
    do {
        m++;
    } until (m >= 5);

    int total = sum_all(3, 1, 2, 3);

    return max + sign + n + m + total;
}
