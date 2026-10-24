/* Syntax analysis: arrays, pointers and function pointers
   (several small programs joined into one file; each part is marked by a comment line) */

/* ---------- part: arrays_and_pointers.c ---------- */
// Covers: integer/char arrays, multidimensional arrays, complex indexing,
// pointers (incl. multi-level), and an argv-style array-of-pointers parameter
int compute_index(int x) {
    if (x <= 1) return x;
    return compute_index(x - 1) + compute_index(x - 2);
}

int main(int argc, char *argv[]) {
    int scores[5];
    int i, total = 0;
    for (i = 0; i < 5; i++) {
        scores[i] = i * 10;
        total += scores[i];
    }

    char name[10];
    name[0] = 'H';
    name[1] = 'i';
    name[2] = '\0';
    char greeting[] = "hello";

    int matrix[10][10];
    int cube[2][2][2];
    int j = 3;
    matrix[i + 1][j * 2 - 1] = 42;
    matrix[compute_index(5)][compute_index(3)] = 100;
    cube[0][1][1] = 7;

    printf("Computed Value: %d\n", compute_index(matrix[0][0]));
    scanf("%d", &matrix[i][j]);

    int x = 5;
    int *p;
    int **pp;
    p = &x;
    pp = &p;
    *p = 10;
    **pp = 20;

    return total;
}

/* ---------- part: test2_structs_pointers_arrays.c ---------- */
typedef int MyInt;

struct Point {
    int x;
    int y;
};

int add(int a, int b) {
    return a + b;
}

int main() {
    struct Point p;
    MyInt x = 5;
    int *ptr;
    int arr[10];
    ptr = &x;
    p.x = 1;
    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }
    if (x > 0) {
        printf("positive\n");
    } else {
        printf("non-positive\n");
    }
    while (x > 0) {
        x = x - 1;
    }
    switch (x) {
        case 0:
            break;
        default:
            break;
    }
    int result = add(x, *ptr);
    return 0;
}

/* ---------- part: test9_pointers_and_function_pointers.c ---------- */

int add(int a, int b) {
    return a + b;
}

int *makeInt() {
    int *p;
    p = new int;
    *p = 42;
    return p;
}

int main(int argc, char **argv) {
    int (*fp)(int, int);
    fp = add;
    int result;
    result = fp(2, 3);

    int *val;
    val = makeInt();

    int x;
    x = argc;

    return 0;
}
