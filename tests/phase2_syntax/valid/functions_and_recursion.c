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
