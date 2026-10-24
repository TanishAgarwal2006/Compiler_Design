// Feature: Functions
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: deep_recursion (recursion depth: sum to 500, Ackermann) ---- */
int deep_recursion_sum(int n) { if (n == 0) return 0; return n + deep_recursion_sum(n - 1); }
int deep_recursion_ack(int m, int n) {
    if (m == 0) return n + 1;
    if (n == 0) return deep_recursion_ack(m - 1, 1);
    return deep_recursion_ack(m - 1, deep_recursion_ack(m, n - 1));
}
int deep_recursion_gcd(int a, int b) { return b == 0 ? a : deep_recursion_gcd(b, a % b); }
int deep_recursion_fib(int n) { return n < 2 ? n : deep_recursion_fib(n - 1) + deep_recursion_fib(n - 2); }
int deep_recursion_main(void) {
    printf("%d\n", deep_recursion_sum(5000));
    printf("%d\n", deep_recursion_ack(2, 3));
    printf("%d\n", deep_recursion_gcd(1071, 462));
    printf("%d\n", deep_recursion_fib(15));
    return 0;
}

/* ---- part: float_and_array_parameters (float returns, int/char/2-D array parameters) ---- */
float float_and_array_parameters_avg(int a[], int n) {
    int i, s = 0;
    for (i = 0; i < n; i++) s += a[i];
    return (float) s / n;
}
void fill(int a[], int n, int v) { int i; for (i = 0; i < n; i++) a[i] = v + i; }
int float_and_array_parameters_trace(int m[][3], int n) {
    int i, t = 0;
    for (i = 0; i < n; i++) t += m[i][i];
    m[0][0] = -1;
    return t;
}
int float_and_array_parameters_length(char s[]) { int n = 0; while (s[n]) n++; return n; }
void upper(char s[]) { int i; for (i = 0; s[i]; i++) if (s[i] >= 'a' && s[i] <= 'z') s[i] -= 32; }
float scale(float x, int k) { return x * k; }
char next(char c) { return c + 1; }
int add(int a, int b) { return a + b; }
void hello(void) { printf("hello\n"); }
int sq(int x) { return x * x; }
int g = 5;
int float_and_array_parameters_bump(void) { g++; return g; }
int float_and_array_parameters_main(void) {
    int a[5], m[3][3] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    char s[] = "mixed Case";
    fill(a, 5, 10);
    printf("%d %d %f\n", a[0], a[4], float_and_array_parameters_avg(a, 5));
    printf("%d ", float_and_array_parameters_trace(m, 3));
    printf("%d\n", m[0][0]);
    printf("%d %s ", float_and_array_parameters_length(s), s);
    upper(s);
    printf("%s %d\n", s, float_and_array_parameters_length("lit"));
    printf("%f %c %d\n", scale(2, 3), next('a'), add('a', 2.9));
    hello();
    printf("%d\n", add(sq(add(1, 2)), sq(2)));
    printf("%d\n", float_and_array_parameters_bump());
    printf("%d\n", float_and_array_parameters_bump());
    float f = scale(1.5, 2) + add(1, 1);
    printf("%f\n", f);
    return 0;
}

/* ---- part: functions (prototypes, arguments, return values, array and string parameters) ---- */
int functions_is_even(int n);
int functions_is_odd(int n);

int functions_fact(int n) {
    if (n <= 1) return 1;
    return n * functions_fact(n - 1);
}

int functions_fib(int n) {
    if (n < 2) return n;
    return functions_fib(n - 1) + functions_fib(n - 2);
}

int functions_is_even(int n) {
    if (n == 0) return 1;
    return functions_is_odd(n - 1);
}

int functions_is_odd(int n) {
    if (n == 0) return 0;
    return functions_is_even(n - 1);
}

int functions_sum(int a[], int n) {
    int i, s = 0;
    for (i = 0; i < n; i++) s += a[i];
    return s;
}

int functions_trace(int m[][3], int rows) {
    int i, t = 0;
    for (i = 0; i < rows; i++) t += m[i][i];
    return t;
}

int functions_length(char s[]) {
    int n = 0;
    while (s[n] != 0) n++;
    return n;
}

void greet(void) {
    printf("hello\n");
}

int functions_main(void) {
    int v[4] = {1, 2, 3, 4};
    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
    char w[] = "recursion";
    greet();
    printf("%d %d %d %d\n", functions_fact(5), functions_fib(10), functions_is_even(10), functions_is_odd(7));
    printf("%d %d %d\n", functions_sum(v, 4), functions_trace(m, 2), functions_length(w));
    return 0;
}

/* ---- part: mutual_recursion (two functions calling each other through prototypes) ---- */
int mutual_recursion_is_even(int n);
int mutual_recursion_is_odd(int n);
int mutual_recursion_fact(int n) { if (n <= 1) return 1; return n * mutual_recursion_fact(n - 1); }
int mutual_recursion_fib(int n) { return n < 2 ? n : mutual_recursion_fib(n - 1) + mutual_recursion_fib(n - 2); }
int mutual_recursion_is_even(int n) { if (n == 0) return 1; return mutual_recursion_is_odd(n - 1); }
int mutual_recursion_is_odd(int n) { if (n == 0) return 0; return mutual_recursion_is_even(n - 1); }
int mutual_recursion_gcd(int a, int b) { return b == 0 ? a : mutual_recursion_gcd(b, a % b); }
int mutual_recursion_ack(int m, int n) {
    if (m == 0) return n + 1;
    if (n == 0) return mutual_recursion_ack(m - 1, 1);
    return mutual_recursion_ack(m - 1, mutual_recursion_ack(m, n - 1));
}
int mutual_recursion_main(void) {
    int i;
    for (i = 0; i <= 10; i++) printf("%d ", mutual_recursion_fact(i));
    printf("\n");
    for (i = 0; i < 15; i++) printf("%d ", mutual_recursion_fib(i));
    printf("\n%d %d %d %d\n", mutual_recursion_is_even(10), mutual_recursion_is_odd(10), mutual_recursion_is_even(7), mutual_recursion_gcd(84, 36));
    printf("%d\n", mutual_recursion_ack(2, 3));
    printf("%d\n", mutual_recursion_fact(mutual_recursion_fib(5)) + mutual_recursion_gcd(mutual_recursion_fact(4), mutual_recursion_fib(8)));
    return 0;
}

/* ---- part: edge_funcs ---- */
int add10(int a,int b,int c,int d,int e,int f,int g,int h,int i,int j){ return a+b+c+d+e+f+g+h+i+j; }
int edge_funcs_fib(int n){ return n < 2 ? n : edge_funcs_fib(n-1) + edge_funcs_fib(n-2); }
int edge_funcs_ack(int m,int n){ if(m==0) return n+1; if(n==0) return edge_funcs_ack(m-1,1); return edge_funcs_ack(m-1, edge_funcs_ack(m,n-1)); }
int isodd(int n);
int iseven(int n){ return n==0 ? 1 : isodd(n-1); }
int isodd(int n){ return n==0 ? 0 : iseven(n-1); }
float edge_funcs_avg(float a, float b){ return (a+b)/2; }
int toint(float f){ return f; }
float tofl(int i){ return i; }
char nxt(char c){ return c + 1; }
void noret(int x){ if (x) return; printf("noret\n"); }
int swapcount = 0;
void edge_funcs_bump(int x){ x = x + 1; swapcount++; }
int val = 5;
int shadow(int val){ return val * 2; }
int edge_funcs_main(){
    printf("%d\n", add10(1,2,3,4,5,6,7,8,9,10));
    printf("%d\n", edge_funcs_fib(15));
    printf("%d\n", edge_funcs_ack(2,3));
    printf("%d %d\n", iseven(10), isodd(7));
    printf("%f\n", edge_funcs_avg(1, 2));
    printf("%d %f %c\n", toint(3.7), tofl(4), nxt('a'));
    noret(0); noret(1);
    int q = 1; edge_funcs_bump(q); printf("%d %d\n", q, swapcount);
    printf("%d %d\n", shadow(4), val);
    { int val = 9; printf("%d\n", val); }
    printf("%d\n", val);
    printf("%d\n", edge_funcs_fib(edge_funcs_fib(5)));
    return 0;
}

/* ---- part: edge_printfn ---- */
void print_int(int v) { printf("<%d>\n", v); }
int read_int() { return 41; }
int edge_printfn_main() { print_int(read_int() + 1); return 0; }

int main(void) {
    printf("== deep_recursion\n");
    deep_recursion_main();
    printf("== float_and_array_parameters\n");
    float_and_array_parameters_main();
    printf("== functions\n");
    functions_main();
    printf("== mutual_recursion\n");
    mutual_recursion_main();
    printf("== edge_funcs\n");
    edge_funcs_main();
    printf("== edge_printfn\n");
    edge_printfn_main();
    return 0;
}
