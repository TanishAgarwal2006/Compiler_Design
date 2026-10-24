/* Syntax analysis: input/output, dynamic memory (new/delete, malloc) and file I/O calls
   (several small programs joined into one file; each part is marked by a comment line) */

/* ---------- part: io_and_input.c ---------- */
// Covers: printf/scanf with multiple arguments, and reading a
// variable-length series of values (command-line-style input)
int main() {
    int a, b, sum;
    printf("Enter two integers: ");
    scanf("%d %d", &a, &b);
    sum = a + b;
    printf("Sum = %d\n", sum);

    int n, i;
    int values[10];
    printf("How many values? ");
    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%d", &values[i]);
    }

    return 0;
}

/* ---------- part: new_delete_and_scope.c ---------- */
// Covers: free-store allocation (new/delete, including array form) and
// scope-resolved (::) access to a base class member.
class Base {
public:
    int value;
    int getValue() { return value; }
};

class Derived : public Base {
public:
    int getBaseValue() { return Base::value; }
};

int main() {
    int *p = new int;
    *p = 42;
    delete p;

    int *arr = new int[10];
    arr[0] = 1;
    delete[] arr;

    Derived d;
    d.value = 7;
    int v = d.getBaseValue();

    int w = Derived::value;

    return 0;
}

/* ---------- part: test6_dynamic_memory_file_io.c ---------- */


int main() {
    int *heap;
    heap = (int *) malloc(10 * 4);
    heap[0] = 42;
    free(heap);

    int *more;
    more = (int *) calloc(5, 4);
    more = (int *) realloc(more, 20);
    free(more);

    FILE *f;
    f = fopen("data.txt", "r");
    fprintf(f, "%d\n", 42);
    fclose(f);

    return 0;
}
