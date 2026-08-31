int main() {
    int i = 0, sum = 0;
    while (i < 10) {
        sum += i;
        i++;
    }
    printf("%d\n", sum);

    // Empty loop bodies
    int a = 1;
    int b = 2;
    while (a < 5) 
        a++;

    while (b < 5); // Semi-colon only body

    return 0;
}
