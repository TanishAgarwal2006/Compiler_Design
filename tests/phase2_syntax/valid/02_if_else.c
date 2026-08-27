int classify(int n) {
    if (n > 0) {
        return 1;
    } else if (n < 0) {
        return -1;
    } else {
        return 0;
    }
}

int main() {
    int r = classify(-5);
    printf("%d\n", r);
    return 0;
}
