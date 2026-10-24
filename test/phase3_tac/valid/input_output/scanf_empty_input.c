// Feature: Input/output
// Covers : scanf on empty input returns -1 and changes nothing (the .in file is empty)
#include <stdio.h>

int main(void) {
    int a = 5;
    char ch = 'z';
    int n = scanf("%d", &a);
    printf("%d %d\n", n, a);
    n = scanf(" %c", &ch);
    printf("%d %c\n", n, ch);
    return 0;
}
