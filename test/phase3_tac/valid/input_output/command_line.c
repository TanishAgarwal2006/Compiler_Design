// Feature: Input/output
// Covers : main(argc, argv), atoi, argv[i][j]
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    int i, total = 0;
    printf("argc=%d\n", argc);
    for (i = 1; i < argc; i++) {
        total += atoi(argv[i]);
        printf("arg %d: %s first=%c\n", i, argv[i], argv[i][0]);
    }
    printf("total=%d\n", total);
    return 0;
}
