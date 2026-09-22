// Covers: reserved keywords, delimiters, arithmetic operators, compound
// assignment, increment/decrement, and relational/logical operators
typedef int Number;

int helper(int x) {
    if (x > 0) {
        return x;
    } else {
        return -x;
    }
}

int main() {
    Number n;
    int arr[3];
    char c;
    void *unused;
    int a = 10, b = 3, r;

    // arithmetic and compound assignment
    r = a + b;
    r = a - b;
    r = a * b;
    r = a / b;
    r = a % b;
    a += 1;
    a -= 1;
    a *= 2;
    a /= 2;
    a %= 2;
    a++;
    a--;
    ++a;
    --a;

    // relational and logical
    r = (a > b) && (a != 0);
    r = (a < b) || (b == a);
    r = !r;
    r = (a <= b);
    r = (a >= b);

    for (n = 0; n < 3; n++) {
        while (n < 1) {
            do {
                break;
            } while (0);
            continue;
        }
    }

    scanf("%d", &n);
    printf("%d\n", helper(n));
    goto end;
end:
    return 0;
}
