// Feature: Arithmetic
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: arithmetic_logical_bitwise (+ - * / %, relational, && || !, & | ^ ~, << >>, comma) ---- */
int arithmetic_logical_bitwise_main(void) {
    int a = 17, b = 5, c;
    c = a + b * 2 - a / b + a % b;
    printf("%d\n", c);
    printf("%d %d %d %d\n", a & b, a | b, a ^ b, ~a);
    printf("%d %d\n", a << 2, a >> 1);
    printf("%d %d %d\n", a > b, a == b, a != b);
    printf("%d %d %d\n", a && b, a || 0, !a);
    a += 3; a -= 1; a *= 2; a /= 3; a %= 7;
    b <<= 2; b >>= 1; b &= 7; b |= 8; b ^= 3;
    printf("%d %d\n", a, b);
    c = a++ + ++b;
    printf("%d %d %d\n", a, b, c);
    c = (a = 1, b = 2, a + b);
    printf("%d\n", c);
    printf("%d\n", -a + +b);
    return 0;
}

/* ---- part: compound_assignment (+= -= *= /= %= <<= >>= &= |= ^= on int, float, char, array elements) ---- */
int compound_assignment_main(void) {
    int x = 100;
    x += 5; printf("%d\n", x);
    x -= 7; printf("%d\n", x);
    x *= 3; printf("%d\n", x);
    x /= 4; printf("%d\n", x);
    x %= 7; printf("%d\n", x);
    x <<= 4; printf("%d\n", x);
    x >>= 2; printf("%d\n", x);
    x &= 0x3C; printf("%d\n", x);
    x |= 0x41; printf("%d\n", x);
    x ^= 0xFF; printf("%d\n", x);
    float f = 2.0f; f += 1; f *= 2.5; f -= 0.5; f /= 2;
    printf("%f\n", f);
    char c = 120; c += 10; printf("%d\n", c);
    int a[3] = {1, 2, 3};
    int i = 0;
    a[i++] += 10; a[i++] *= 5; a[i] <<= 2;
    printf("%d %d %d %d\n", a[0], a[1], a[2], i);
    int p = 3, q = 4; p = q = p + q; printf("%d %d\n", p, q);
    return 0;
}

/* ---- part: division_modulo_shift (/ and % with negative operands, shifts) ---- */
int division_modulo_shift_main(void) {
    printf("%d %d %d %d\n", 7 / 2, -7 / 2, 7 / -2, -7 / -2);
    printf("%d %d %d %d\n", 7 % 3, -7 % 3, 7 % -3, -7 % -3);
    printf("%d %d %d\n", -16 >> 2, 1 << 30, 5 >> 1);
    printf("%d %d %d\n", ~0, ~5, -(-8));
    printf("%d %d\n", 5 & 3 | 8, 5 ^ 3 ^ 3);
    printf("%d %d %d\n", !0, !5, !!7);
    printf("%d %d\n", 3 < 4 == 1, 2 + 3 * 4 - 6 / 2);
    return 0;
}

/* ---- part: increment_decrement (prefix/postfix ++ --, chained assignment, assignment as a value) ---- */
int increment_decrement_main(void) {
    int a = 5, b, c;
    b = a++;
    c = ++a;
    printf("%d %d %d\n", a, b, c);
    b = a--;
    c = --a;
    printf("%d %d %d\n", a, b, c);
    a++;
    ++a;
    a--;
    --a;
    printf("%d\n", a);
    a = 10;
    a += 5;
    a -= 3;
    a *= 4;
    a /= 5;
    a %= 7;
    printf("%d\n", a);
    a = 6;
    a <<= 3;
    a >>= 1;
    a &= 29;
    a |= 64;
    a ^= 5;
    printf("%d\n", a);
    a = b = c = 3;
    printf("%d %d %d\n", a, b, c);
    a = (b = 4) + (c = 5);
    printf("%d %d %d\n", a, b, c);
    a = 3;
    b = a++ * 2 + 1;
    printf("%d %d\n", a, b);
    {
        char ch = 'a';
        float f = 1.5;
        float g;
        ch++;
        ch += 2;
        f++;
        f += 2;
        f *= 2;
        f -= 0.5;
        f /= 2;
        g = f--;
        printf("%c %f %f\n", ch, f, g);
    }
    return 0;
}

/* ---- part: int_expressions (precedence, unary + - ~ !, truncating int division) ---- */
int int_expressions_main(void) {
    int a = 17, b = 5, c = -7, d = 3;
    int r;

    r = a + b * d - a / b + a % b;
    printf("%d\n", r);
    printf("%d %d %d %d\n", a / b, a % b, c / d, c % d);
    printf("%d %d %d %d\n", -a / b, -a % b, a / -b, a % -b);
    printf("%d %d %d %d\n", a & b, a | b, a ^ b, ~a);
    printf("%d %d %d\n", a << 2, a >> 1, c >> 1);
    printf("%d %d %d %d %d %d\n", a > b, a < b, a >= 17, a <= 16, a == b, a != b);
    printf("%d %d %d\n", !a, !0, !!c);
    printf("%d %d\n", -a, +c);
    r = (a + b) * (c - d);
    printf("%d\n", r);
    r = a - b - d;
    printf("%d\n", r);
    r = a / b / 2;
    printf("%d\n", r);
    printf("%d %d\n", a + b << 1, a & b == 5);
    printf("%d\n", (r = 9, r + 1));
    r = (a, b, c);
    printf("%d\n", r);
    return 0;
}

/* ---- part: int_wraparound (32-bit wrap-around on overflow) ---- */
int int_wraparound_main(void) {
    int big = 2147483647;
    int low = -2147483647 - 1;
    int x;
    x = big + 1;
    printf("%d\n", x);
    x = big * 2;
    printf("%d\n", x);
    x = -low;
    printf("%d\n", x);
    x = low - 1;
    printf("%d\n", x);
    x = 65536;
    x = x * x;
    printf("%d\n", x);
    x = 1;
    x = x << 31;
    printf("%d\n", x);
    x = x >> 31;
    printf("%d\n", x);
    return 0;
}

/* ---- part: short_circuit (&& and || skip their right side; ! on values) ---- */
int n = 0;
int short_circuit_main(void) {
    int a = 0, b = 5, c;
    if (a && (b = 9)) printf("x\n");
    if (a || (b = 7)) printf("b=%d\n", b);
    if (b > 3 && !a || (n = 1)) printf("n=%d\n", n);
    c = (a && b) || (b && !a);
    printf("c=%d\n", c);
    c = a || 0;
    printf("c=%d\n", c);
    c = (b == 7) && (a < 1) && (b != 3);
    printf("c=%d\n", c);
    float f = 0.0;
    if (f) printf("f true\n"); else printf("f false\n");
    f = 2.5;
    if (f && b) printf("both\n");
    if (!(a < b && f > 1.0)) printf("no\n"); else printf("yes\n");
    while (a < 3 && b > 0) { a++; b -= 3; }
    printf("a=%d b=%d\n", a, b);
    if (1 || (a = 99)) printf("a=%d\n", a);
    return 0;
}

/* ---- part: edge_arith ---- */
int edge_arith_main() {
    char c = 127; c++; printf("%d\n", c);
    char d = 200; printf("%d\n", d);
    char e = -129; printf("%d\n", e);
    int a = -7, b = 2;
    printf("%d %d %d %d\n", a / b, a % b, -a / b, a % -b);
    printf("%d %d %d\n", a >> 1, a << 2, 1 << 31);
    printf("%d\n", 2147483647 + 1);
    printf("%d\n", -2147483647 - 1);
    int big = 2000000000; printf("%d\n", big * 2);
    printf("%d\n", 0x7fffffff);
    printf("%d\n", 0xffffffff);
    printf("%d\n", 4294967295U);
    printf("%d\n", 077);
    printf("%d\n", 0b1011);
    printf("%d\n", 'a' + 1);
    printf("%c\n", 'a' + 1);
    int x = 3.9; printf("%d\n", x);
    int y = -3.9; printf("%d\n", y);
    float f = 1/2; printf("%f\n", f);
    float g = 1/2.0; printf("%f\n", g);
    float h = 7; printf("%f\n", h / 2);
    printf("%d\n", (int)3.99f);
    printf("%d\n", 5 > 3 == 1);
    printf("%d\n", 1 + 2 * 3 << 1 & 7 | 8 ^ 2);
    int p, q, r; p = q = r = 5; printf("%d %d %d\n", p, q, r);
    int z = (1, 2, 3); printf("%d\n", z);
    printf("%d\n", !5 + !0 + !!7);
    printf("%d %d\n", ~0, ~5);
    printf("%d\n", -(-3));
    printf("%d\n", 10 - 3 - 2);
    printf("%d\n", 100 / 10 / 5);
    printf("%d\n", 2 * 3 % 4);
    printf("%d\n", 1 ? 2 : 3);
    printf("%d\n", 0 ? 2 : 0 ? 3 : 4);
    int u = 5; u += 3; u -= 1; u *= 2; u /= 3; u %= 3; u <<= 3; u >>= 1; u &= 6; u |= 9; u ^= 3; printf("%d\n", u);
    int s = 10; s = s++ > 5 ? 1 : 2; printf("%d\n", s);
    return 0;
}

/* ---- part: edge_incdec ---- */
int edge_incdec_main() {
    int a[5] = {1,2,3,4,5};
    int i = 0;
    a[i++] += 10; printf("%d %d\n", i, a[0]);
    a[i++] *= 3; printf("%d %d\n", i, a[1]);
    a[++i] -= 1; printf("%d %d\n", i, a[3]);
    a[i--]++; printf("%d %d\n", i, a[3]);
    int j = 0; int k = a[j++] + a[j++]; printf("%d\n", j);
    char s[4] = {'a','b','c','d'}; int n = 0;
    s[n++]++; printf("%c%d\n", s[0], n);
    int m[2][2] = {{1,2},{3,4}}; int r = 0, c = 0;
    m[r++][c++] += 5; printf("%d %d %d\n", r, c, m[0][0]);
    int x = 5; x = x++ + 1; printf("%d\n", x > 0);
    float f = 1.5; f++; printf("%f\n", f);
    f--; --f; printf("%f\n", f);
    char ch = 'a'; ch++; printf("%c\n", ch);
    int t = 3; printf("%d %d\n", t++, t); 
    return 0;
}

int main(void) {
    printf("== arithmetic_logical_bitwise\n");
    arithmetic_logical_bitwise_main();
    printf("== compound_assignment\n");
    compound_assignment_main();
    printf("== division_modulo_shift\n");
    division_modulo_shift_main();
    printf("== increment_decrement\n");
    increment_decrement_main();
    printf("== int_expressions\n");
    int_expressions_main();
    printf("== int_wraparound\n");
    int_wraparound_main();
    printf("== short_circuit\n");
    short_circuit_main();
    printf("== edge_arith\n");
    edge_arith_main();
    printf("== edge_incdec\n");
    edge_incdec_main();
    return 0;
}
