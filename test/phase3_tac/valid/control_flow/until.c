// Feature: Control flow
// Covers : until and do-until loops (extension, not C)
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int i = 0;
    int s = 0;
    until (i == 5) {
        s += i;
        i++;
    }
    do {
        s += 10;
        i--;
    } until (i <= 2);
    printf("%d\n", s);
    return 0;
}
