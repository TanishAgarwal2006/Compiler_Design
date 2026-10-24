#include <stdio.h>
/* A typedef name used by the very next token after its ';' (this once failed to parse). */
typedef int Number;
Number total = 5;
typedef int Row[3];
Row grid = {1, 2, 3};
typedef Number Count, Size;
Size size = 7;
volatile int vol = 2;
_Bool flag = 1;

int main(void) {
    Count c = total + size;
    printf("%d %d %d %d %d\n", c, grid[0] + grid[2], vol, flag, (int)sizeof(Row));
    return 0;
}
