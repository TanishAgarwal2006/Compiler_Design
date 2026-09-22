// Covers: function call arguments missing a comma separator
int add(int a, int b) {
    return a + b;
}

int main() {
    int r = add(3 4);
    return 0;
}
