/* Every reserved keyword and delimiter recognized by the lexer */
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
