// Feature: Types
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* ---- part: bool (bool, true, false) ---- */
bool is_even(int n) { return n % 2 == 0; }
int bool_main(void) {
    bool a = true, b = false;
    int sum = a + b + true;
    printf("%d %d %d\n", a, b, sum);
    printf("%d %d\n", is_even(4), is_even(7));
    bool c = 1;
    printf("%d\n", c);
    if (a && !b) printf("yes\n");
    b = !b;
    printf("%d\n", b);
    return 0;
}

/* ---- part: char (char: signed 8-bit, narrowing on store, promotion in expressions, casts) ---- */
int char_main(void) {
    char c = 'A';
    char d = 200;
    char e;
    int i = 300;
    e = i;
    printf("%d %d %d\n", c, d, e);
    c = c + 1;
    printf("%c %d\n", c, c);
    c = 127;
    c++;
    printf("%d\n", c);
    d = d + d;
    i = d * 2;
    printf("%d %d\n", d, i);
    printf("%d %d\n", (char)321, (int)'a' + 1);
    c = 'a';
    printf("%c%c%c\n", c, c + 1, c + 2);
    c = 'z' - 'a';
    printf("%d\n", c);
    c += 300;
    printf("%d\n", c);
    c = -1;
    printf("%d %d\n", c, c < 0);
    e = 'x';
    i = e - 'a';
    printf("%d\n", i);
    return 0;
}

/* ---- part: float (float arithmetic, int/float mixing, casts, comparisons) ---- */
int float_main(void) {
    float a = 1.5, b = 2.25, c;
    int i = 7, j;
    c = a + b;
    printf("%f\n", c);
    c = a * b - 0.5;
    printf("%f\n", c);
    c = i / 2;
    printf("%f\n", c);
    c = i / 2.0;
    printf("%f\n", c);
    c = (float)i / 2;
    printf("%f\n", c);
    j = a;
    printf("%d\n", j);
    c = -2.7;
    j = c;
    printf("%d %d\n", j, (int)(b * 4));
    printf("%d %d %d\n", a < b, a > b, a == 1.5);
    printf("%d %d %d\n", !a, !(a - a), i > a);
    c = -a;
    printf("%f %f\n", c, -b);
    a = 0.1;
    b = 0.2;
    c = a + b;
    printf("%f %f\n", c, c * 3);
    c = 1.0;
    c = c / 3;
    printf("%f %f\n", c, c * 3);
    a = 2.5;
    a++;
    a += 2;
    a *= 2;
    a -= 0.5;
    a /= 2;
    printf("%f\n", a);
    i += 1.5;
    printf("%d\n", i);
    i *= 0.5;
    printf("%d\n", i);
    i /= 3.0;
    printf("%d\n", i);
    printf("%d %d\n", (int)3.99, (int)-3.99);
    {
        char ch = 65.7;
        printf("%c\n", ch);
    }
    return 0;
}

/* ---- part: float_precision (single-precision rounding of float results) ---- */
int float_precision_main(void) {
    float a = 0.1f, b = 0.2f, c = a + b;
    printf("%f %d\n", c, c == 0.3f);
    float neg = -3.75f;
    printf("%f %d %d\n", neg, (int) neg, (int)(neg * -1));
    if (a) printf("nonzero\n");
    float z = 0.0f;
    if (!z) printf("zero\n");
    int i; float s = 0;
    for (i = 1; i <= 4; i++) s += 1.0f / i;
    printf("%f\n", s);
    float f = 7; int k = 2;
    printf("%f %f\n", f / k, k / 4.0f);
    printf("%d\n", 7 / 2 * 2.0 > 6.5);
    int t = 3.99f; printf("%d\n", t);
    float big = 16777216.0f; big = big + 1; printf("%f\n", big);
    float r = (float) 1 / 3; printf("%f\n", r);
    return 0;
}

/* ---- part: number_literals (hex, octal, binary, char and escape literals) ---- */
int number_literals_main(void) {
    int h = 0x1F, o = 017, b = 0b101;
    char c1 = 'A', c2 = '\n', c3 = '\\', c4 = '\'', c5 = '\0', c6 = '\t';
    printf("%d %d %d\n", h, o, b);
    printf("%d %d %d %d %d %d\n", c1, c2, c3, c4, c5, c6);
    printf("tab[\t] quote[\"] backslash[\\] pct[%%]\n");
    float f = 1.5f, g = .25, e = 1e2, k = 2.5e-1;
    printf("%f %f %f %f\n", f, g, e, k);
    printf("%d\n", 'a' + 1);
    printf("%c%c%c\n", 72, 'i', 33);
    return 0;
}

/* ---- part: type_aliases_static_void (double (same as float), long/short/unsigned/signed (same as int), static global and function, void function with "return;") ---- */
static int counter = 10;
static int twice(int x) { return x * 2; }

void bump(int by) {
    if (by == 0)
        return;
    counter += by;
}

int type_aliases_static_void_main(void) {
    double d = 2.5;
    long big = 100000;
    short s = 12;
    unsigned u = 7;
    signed int n = -3;
    d = d * 2 + 0.25;
    bump(0);
    bump(5);
    printf("%f %d %d %d %d\n", d, big, s, u, n);
    printf("%d %d\n", counter, twice(counter));
    printf("%i %i\n", s + u, -n);
    return 0;
}

/* ---- part: edge_float ---- */
int edge_float_main() {
    float a = 0.5, b = 0.25;
    printf("%f %f %f %f\n", a + b, a - b, a * b, a / b);
    float c = 1.0 / 3; printf("%f\n", c);
    float d = 100000.5; printf("%f\n", d);
    float e = 3; e = e / 2; printf("%f\n", e);
    printf("%d\n", a > b); printf("%d\n", a == 0.5); printf("%d\n", a != b);
    int i = 7; float g = i / 2; printf("%f\n", g);
    float h = i / 2.0; printf("%f\n", h);
    printf("%f\n", -a); printf("%d\n", !a); printf("%d\n", !0.0);
    float k = 1e3; printf("%f\n", k);
    float m = 2.5e-1; printf("%f\n", m);
    printf("%f\n", .5);
    printf("%f\n", 5.);
    int t = (int)(2.5 + 2.5); printf("%d\n", t);
    float n = (float)7 / 2; printf("%f\n", n);
    float acc = 0; int q; for (q = 0; q < 10; q++) acc += 0.5; printf("%f\n", acc);
    printf("%f\n", 1.0f); printf("%f\n", 123456.0f);
    double dd = 3.25; printf("%f\n", dd * 2);
    return 0;
}

/* ---- part: edge_bool_char ---- */
int edge_bool_char_main() {
    bool t = true, f = false; printf("%d %d\n", t, f);
    bool b = 5; printf("%d\n", b);
    bool c = 3 > 2; printf("%d\n", c);
    bool d = 0.5; printf("%d\n", d);
    b = 7; printf("%d\n", b == 1);
    printf("%d\n", t && !f);
    char x = 'a'; x += 1; printf("%c %d\n", x, x);
    char y = x - 'a'; printf("%d\n", y);
    char z = 300; printf("%d\n", z);
    printf("%d %d %d %d\n", '\n', '\t', '\0', '\\');
    printf("%d %d %d\n", '\'', '"', '\a');
    printf("%d %d %d\n", '\101', '\x41', '\?');
    printf("tab\there\\n \"q\" 'single' \x41\102 %c\n", 'Z');
    char s[8] = "a\tb"; printf("%s|\n", s);
    printf("%d\n", 'a' < 'b');
    int n = 'a' * 2; printf("%d\n", n);
    unsigned u = 3; u -= 5; printf("%d\n", u);
    long l = 100000; l *= 100000; printf("%d\n", l);
    return 0;
}

int main(void) {
    printf("== bool\n");
    bool_main();
    printf("== char\n");
    char_main();
    printf("== float\n");
    float_main();
    printf("== float_precision\n");
    float_precision_main();
    printf("== number_literals\n");
    number_literals_main();
    printf("== type_aliases_static_void\n");
    type_aliases_static_void_main();
    printf("== edge_float\n");
    edge_float_main();
    printf("== edge_bool_char\n");
    edge_bool_char_main();
    return 0;
}
