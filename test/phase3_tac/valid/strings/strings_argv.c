#include <stdio.h>
char *greeting = "hello";
char msg[] = "world";
int len(char *s) { int n = 0; while (s[n]) n++; return n; }
int same(char a[], char b[]) { int i = 0; while (a[i] && a[i] == b[i]) i++; return a[i] == b[i]; }
void rev(char s[]) { int n = len(s), i; for (i = 0; i < n / 2; i++) { char t = s[i]; s[i] = s[n - 1 - i]; s[n - 1 - i] = t; } }
int main(int argc, char *argv[]) {
    char *p = "literal"; printf("%s %d %c\n", p, len(p), p[1]);
    printf("%s %s %d\n", greeting, msg, len(msg));
    char buf[20] = "abcdef"; rev(buf); printf("%s\n", buf);
    printf("%d %d\n", same("ab", "ab"), same("ab", "ac"));
    char *q = greeting; printf("%c\n", q[4]);
    printf("%s\n", "a\tb\\c\"d");
    printf("%d\n", argc);
    if (argc > 1) printf("%s %d\n", argv[1], atoi(argv[1]) + 1);
    char e[1] = ""; printf("[%s] %d\n", e, len(e));
    printf("%s", "no newline"); printf("\n");
    printf("%d\n", atoi("  -42abc"));
    printf("%d\n", atoi("abc"));
    return 0;
}
