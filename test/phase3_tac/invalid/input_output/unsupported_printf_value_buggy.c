// Expected error: using the value returned by printf
#include <stdio.h>

int main(void) {
    int n = printf("hi\n");
    return 0;
}
