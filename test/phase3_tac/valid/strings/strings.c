// Feature: Strings
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: string_literals (char * literals, indexing, passing to functions, %s) ---- */
int count_char(char *s, char c) {
    int i = 0, n = 0;
    while (s[i] != 0) {
        if (s[i] == c) n++;
        i++;
    }
    return n;
}

int string_literals_main(void) {
    char *msg = "banana";
    char buf[8] = "apple";
    printf("%s %d %d\n", msg, count_char(msg, 'a'), count_char(buf, 'p'));
    msg = buf;
    printf("%s %c\n", msg, msg[0]);
    return 0;
}

/* ---- part: string_variables (char * variables: copy and reassign) ---- */
char *msg = "global string";

int string_variables_main(void) {
    char *s = "hello";
    char *t;
    printf("%s %s\n", msg, s);
    t = s;
    s = "world";
    printf("%s %s\n", s, t);
    msg = "changed";
    printf("%s\n", msg);
    return 0;
}

int main(void) {
    printf("== string_literals\n");
    string_literals_main();
    printf("== string_variables\n");
    string_variables_main();
    return 0;
}
