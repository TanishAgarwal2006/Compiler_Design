// Feature: Input Output
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: printf (printf with %d %c %f %s %%, escapes, several conversions) ---- */
int printf_main(void) {
    int n = -5;
    char c = 'q';
    float f = 3.25;
    printf("plain text only\n");
    printf("%d\n", 42);
    printf("%c%c%c\n", 'a', 98, 'c');
    printf("%f\n", 2.5);
    printf("%s|%s\n", "left", "right");
    printf("100%%\n");
    printf("tab\there \"quoted\" back\\slash\n");
    printf("%d%d%d\n", 1, 2, 3);
    printf("");
    printf("%d", n);
    printf("\n");
    printf("n=%d c=%c f=%f done\n", n, c, f);
    printf("%s %s\n", "same", "same");
    return 0;
}

/* ---- part: printf_scanf (reading with scanf, printing results) ---- */
int printf_scanf_main(void) {
    int n;
    char c;
    float f;
    char word[20];
    int nums[3];
    int i;
    scanf("%d", &n);
    scanf(" %c", &c);
    scanf("%f", &f);
    scanf("%s", word);
    for (i = 0; i < 3; i++) scanf("%d", &nums[i]);
    printf("n=%d c=%c f=%f word=%s 100%%\n", n, c, f, word);
    printf("%d %d %d\n", nums[0], nums[1], nums[2]);
    return 0;
}

/* ---- part: scanf_i_format (%i in scanf and printf, reading two numbers separated by white space) ---- */
int scanf_i_format_main(void) {
    int a, b;
    scanf("%i %i", &a, &b);
    printf("%i + %i = %i\n", a, b, a + b);
    return 0;
}

/* ---- part: scanf_string_then_char (%s followed by %c, %c after %d, white space handling) ---- */
int scanf_string_then_char_main(void) {
    char word[20];
    char c;
    int n;
    scanf("%s %c", word, &c);
    printf("[%s] [%c]\n", word, c);
    scanf("%d %c", &n, &c);
    printf("%d [%c]\n", n, c);
    return 0;
}

/* ---- part: scanf_variants (scanf into array elements, %c after %d) ---- */
int scanf_variants_main(void) {
    int a, b, i, v[3];
    char c, d, w[16];
    float f;
    scanf("%d %d", &a, &b);
    scanf("%c", &c);
    scanf(" %c", &d);
    scanf("%f", &f);
    scanf("%s", w);
    for (i = 0; i < 3; i++) scanf("%d", &v[i]);
    printf("%d %d [%d] %c %f %s\n", a, b, c, d, f, w);
    printf("%d\n", v[0] + v[1] * v[2]);
    return 0;
}

/* ---- part: edge_io ---- */
int edge_io_main() {
    int a, b; char c; float f; char s[20]; int arr[3]; char name[10];
    int n = scanf("%d %d", &a, &b); printf("%d %d %d\n", n, a, b);
    n = scanf(" %c", &c); printf("%d %c\n", n, c);
    n = scanf("%f", &f); printf("%d %f\n", n, f);
    n = scanf("%s", s); printf("%d %s\n", n, s);
    n = scanf("%d%d%d", &arr[0], &arr[1], &arr[2]); printf("%d %d %d %d\n", n, arr[0], arr[1], arr[2]);
    n = scanf("%d %c %s", &a, &c, name); printf("%d %d %c %s\n", n, a, c, name);
    n = scanf("%i", &a); printf("%d %d\n", n, a);
    n = scanf("%d", &a); printf("%d %d\n", n, a);
    n = scanf("%d", &a); printf("%d\n", n);
    printf("%d%%|%c|%s|%f|\n", 5, 'x', "str", 1.5);
    return 0;
}

/* ---- part: scanf_return_value (scanf returns the number of values read; a failed read leaves the variable unchanged; reading until input ends) ---- */
int scanf_return_value_main(void) {
    int a = 5, b = 6, n, sum = 0;
    n = scanf("%d %d", &a, &b);
    printf("read %d: %d %d\n", n, a, b);
    while (scanf("%d", &a) == 1)
        sum += a;
    printf("sum=%d last=%d\n", sum, a);
    return 0;
}

int main(void) {
    printf("== printf\n");
    printf_main();
    printf("== printf_scanf\n");
    printf_scanf_main();
    printf("== scanf_i_format\n");
    scanf_i_format_main();
    printf("== scanf_string_then_char\n");
    scanf_string_then_char_main();
    printf("== scanf_variants\n");
    scanf_variants_main();
    printf("== edge_io\n");
    edge_io_main();
    printf("== scanf_return_value\n");
    scanf_return_value_main();
    return 0;
}
