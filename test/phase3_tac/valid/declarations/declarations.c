// Feature: Declarations
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: global_initializers (constant initialisers, constant folding) ---- */
#define N 4
int base = 10 + 5 * 2;
float ratio = 2.5;
char global_initializers_letter = 'Z';
int table[4] = {1, 2, 3, 4};
int grid[2][2] = {{1, 2}, {3, 4}};
char name[] = "global";
int global_initializers_size = sizeof(int) * 4;

int global_initializers_main(void) {
    printf("%d %f %c %d %d %s %d\n", base, ratio, global_initializers_letter, table[3], grid[1][0], name, global_initializers_size);
    return 0;
}

/* ---- part: globals_typedef_enum_const (globals, typedef, enum, const, sizeof together) ---- */
typedef int Number;
typedef float Real;
enum Mode { OFF, ON = 5, AUTO };

const int globals_typedef_enum_const_LIMIT = 10;
int globals_typedef_enum_const_x = 100;
Number total = globals_typedef_enum_const_LIMIT * 2 + 1;
Real half = 0.5;
char grade = 'B';
int globals_typedef_enum_const_size = sizeof(int) * 4 + sizeof(char);
int unset;

int globals_typedef_enum_const_main(void) {
    enum Mode m = AUTO;
    Number n = 4;
    Real r = n;
    const int k = 3;
    int y = k * 2;
    printf("%d %d %f %c %d %d\n", total, globals_typedef_enum_const_LIMIT, half, grade, globals_typedef_enum_const_size, unset);
    printf("%d\n", globals_typedef_enum_const_x);
    int globals_typedef_enum_const_x = 5;
    printf("%d\n", globals_typedef_enum_const_x);
    {
        int globals_typedef_enum_const_x = 7;
        globals_typedef_enum_const_x = globals_typedef_enum_const_x + 1;
        printf("%d\n", globals_typedef_enum_const_x);
        {
            int globals_typedef_enum_const_x = 9;
            printf("%d\n", globals_typedef_enum_const_x);
        }
        printf("%d\n", globals_typedef_enum_const_x);
    }
    printf("%d\n", globals_typedef_enum_const_x);
    printf("%d %d %d %d\n", OFF, ON, AUTO, m);
    printf("%d %f %d\n", n, r, y);
    total = total + 1;
    grade = grade + 1;
    unset = total;
    printf("%d %c %d\n", total, grade, unset);
    return 0;
}

/* ---- part: scopes_nested_blocks (three nested blocks, for-scope, self-initialisation) ---- */
int scopes_nested_blocks_x = 1;
int f(void) { return scopes_nested_blocks_x; }
int scopes_nested_blocks_main(void) {
    int scopes_nested_blocks_x = 2;
    { int scopes_nested_blocks_x = 3; { int scopes_nested_blocks_x = 4; printf("%d ", scopes_nested_blocks_x); } printf("%d ", scopes_nested_blocks_x); }
    printf("%d %d\n", scopes_nested_blocks_x, f());
    for (int scopes_nested_blocks_x = 7; scopes_nested_blocks_x < 8; scopes_nested_blocks_x++) printf("%d ", scopes_nested_blocks_x);
    printf("%d\n", scopes_nested_blocks_x);
    int y = y = 5; printf("%d\n", y);
    return 0;
}

/* ---- part: scopes_shadowing (locals shadowing globals, inner blocks, parameters) ---- */
int scopes_shadowing_x = 100;

int shadow(int scopes_shadowing_x) {
    int y = scopes_shadowing_x + 1;
    {
        int y = 50;
        y = y + scopes_shadowing_x;
        printf("inner y = %d\n", y);
    }
    return y;
}

int scopes_shadowing_main(void) {
    int scopes_shadowing_x = 5;
    printf("%d\n", shadow(scopes_shadowing_x));
    {
        int scopes_shadowing_x = 7;
        printf("%d\n", scopes_shadowing_x);
    }
    printf("%d\n", scopes_shadowing_x);
    return 0;
}

/* ---- part: typedef_enum_const (typedef (scalar and array), enum values, const as array size) ---- */
typedef int Count;
typedef char Letter;
typedef int Row[4];

enum Color { typedef_enum_const_RED, typedef_enum_const_GREEN = 5, typedef_enum_const_BLUE };

const int SIZE = 3;

int typedef_enum_const_main(void) {
    Count c = typedef_enum_const_BLUE;
    Letter ch = 'A';
    Row r;
    int table[SIZE];
    int i;
    for (i = 0; i < 4; i++) r[i] = i * c;
    for (i = 0; i < SIZE; i++) table[i] = typedef_enum_const_RED + typedef_enum_const_GREEN + i;
    printf("%d %c %d %d\n", c, ch, r[3], table[2]);
    printf("%d\n", (int)sizeof(Row));
    return 0;
}

/* ---- part: edge_decl ---- */
typedef int number;
typedef float real;
typedef char edge_decl_letter;
typedef number counter;
typedef int row[3];
enum color { edge_decl_RED, edge_decl_GREEN = 5, edge_decl_BLUE };
enum { A = 1 << 2, B = A + 1, C = sizeof(int) };
const int edge_decl_LIMIT = 10;
const float PI = 3.5;
int gx = 3 + 4 * 2;
float gy = 2 * 1.5;
char gc = 'A' + 2;
int gz;
static int hidden = 7;
static int helper(int v) { return v + hidden; }
extern int ext_decl;
int ext_decl = 12;
int edge_decl_t1 = 100;
int edge_decl_L1 = 200;
int edge_decl_main() {
    number n = 5; real r = 2.5; edge_decl_letter l = 'z'; counter c = 9;
    printf("%d %f %c %d\n", n, r, l, c);
    enum color col = edge_decl_BLUE; printf("%d %d %d %d\n", edge_decl_RED, edge_decl_GREEN, col, A + B + C);
    printf("%d %f %d %f %c %d\n", edge_decl_LIMIT, PI, gx, gy, gc, gz);
    printf("%d %d\n", helper(1), ext_decl);
    int t2 = edge_decl_t1 + edge_decl_L1; printf("%d\n", t2);
    row rr; rr[0] = 1; rr[2] = 3; printf("%d\n", rr[0] + rr[2]);
    int x = 1; { int x = 2; { int x = 3; printf("%d ", x); } printf("%d ", x); } printf("%d\n", x);
    for (int x = 10; x < 12; x++) printf("%d ", x); printf("%d\n", x);
    int y = 5; { int y = y + 1; printf("%d\n", y > 0); }
    printf("%d\n", (int)sizeof(number) + (int)sizeof(edge_decl_letter) + (int)sizeof(real));
    switch (col) { case edge_decl_BLUE: printf("blue\n"); break; case edge_decl_RED: break; }
    char arr[C]; printf("%d\n", (int)sizeof(arr));
    int e = 3, f = e * edge_decl_LIMIT; printf("%d\n", f);
    return 0;
}

/* ---- part: edge_names ---- */
int edge_names_t1 = 1;
int t2(int t3) { int edge_names_t1 = t3 + 1; return edge_names_t1; }
int edge_names_L1(int edge_names_x) { return edge_names_x * 2; }
int edge_names_x = 10;
int edge_names_main() {
    int edge_names_t1 = 5, t3 = 6, L2 = 7, x1 = 8;
    int x2 = edge_names_t1 + t3 + L2 + x1;
    printf("%d %d %d\n", x2, t2(3), edge_names_L1(4));
    { int edge_names_x = 3; { int edge_names_x = edge_names_x + 1; printf("%d\n", edge_names_x > 0); } printf("%d\n", edge_names_x); }
    printf("%d\n", edge_names_x);
    goto L1_end; L1_end: printf("label\n");
    int main_ = 3; printf("%d\n", main_);
    int param = 2, call = 3, goto_ = 4, local = 5, temp = 6, endfunc = 7, func = 8, global = 9;
    printf("%d\n", param + call + goto_ + local + temp + endfunc + func + global);
    return 0;
}

int main(void) {
    printf("== global_initializers\n");
    global_initializers_main();
    printf("== globals_typedef_enum_const\n");
    globals_typedef_enum_const_main();
    printf("== scopes_nested_blocks\n");
    scopes_nested_blocks_main();
    printf("== scopes_shadowing\n");
    scopes_shadowing_main();
    printf("== typedef_enum_const\n");
    typedef_enum_const_main();
    printf("== edge_decl\n");
    edge_decl_main();
    printf("== edge_names\n");
    edge_names_main();
    return 0;
}
