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
