int main() {
    int scores[5];
    int i, total = 0;
    for (i = 0; i < 5; i++) {
        scores[i] = i * 10;
        total += scores[i];
    }
    printf("%d\n", total);
    return 0;
}
