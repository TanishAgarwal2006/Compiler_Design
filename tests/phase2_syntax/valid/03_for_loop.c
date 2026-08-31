int main() {
    int i, sum = 0;
    for (i = 0; i < 10; i++) {
        sum += i;
    }
    printf("%d\n", sum);

    // Omitted expressions in for-loop
    for (;;) {
        break;
    }
    return 0;
}
