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

    // Dangling else test
    int a = 1;
    int b = 2;
    int c = 3;
    if (a == 1)
        if (b == 2)
            c = 10;
    else
        c = 20; // Parser must attach this to 'if (b == 2)'
    return 0;
}
