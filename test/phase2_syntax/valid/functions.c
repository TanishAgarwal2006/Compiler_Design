/* Syntax analysis: functions, recursion, prototypes, overloads
   (several small programs joined into one file; each part is marked by a comment line) */

/* ---------- part: functions_and_recursion.c ---------- */
// Covers: function calls with arguments, recursion, function pointers,
// an empty "(void)" parameter list, and unnamed (abstract) parameters
int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// declared with unnamed parameters, defined with named ones
int multiply(int, int);
int multiply(int a, int b) {
    return a * b;
}

int get_answer(void) {
    return 42;
}

int main(void) {
    int result = add(3, 4);
    printf("%d\n", result);
    printf("%d\n", factorial(5));
    printf("%d\n", fibonacci(10));
    printf("%d\n", multiply(3, 4));
    printf("%d\n", get_answer());

    int (*op)(int a, int b);
    op = add;
    result = op(3, 4);
    op = subtract;
    result = op(10, 2);

    return result;
}

/* ---------- part: test10_forward_references.c ---------- */


int main() {
    goto done;
    int x;
    x = 1;
done:
    return add(1, 2);
}

int add(int a, int b) {
    return a + b;
}

/* ---------- part: test12_function_overloading.c ---------- */


int add(int a, int b) {
    return a + b;
}
int add(int a, int b, int c) {
    return a + b + c;
}

int combine(int a, int b) {
    return a + b;
}
int combine(char a, char b) {
    return a + b;
}

int main() {
    int r1;
    r1 = add(1, 2);
    int r2;
    r2 = add(1, 2, 3);

    int r3;
    r3 = combine(1, 2);
    char x;
    char y;
    int r4;
    r4 = combine(x, y);

    return 0;
}
