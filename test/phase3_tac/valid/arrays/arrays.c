// Feature: Arrays
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: array_edge_cases (size-1 arrays, partial and nested initialisers, 3-D globals) ---- */
int array_edge_cases_g2[2][3] = {{1, 2, 3}, {4, 5, 6}};
int g3[2][2][2] = {{{1,2},{3,4}},{{5,6},{7,8}}};
char array_edge_cases_gs[] = "global";
int part[5] = {1, 2};
int sumrow(int r[], int n) { int i, s = 0; for (i = 0; i < n; i++) s += r[i]; return s; }
int array_edge_cases_main(void) {
    int i, j, k;
    int m[3][4];
    for (i = 0; i < 3; i++) for (j = 0; j < 4; j++) m[i][j] = i * 10 + j;
    printf("%d %d %d\n", m[2][3], m[1][0], m[0][2]);
    printf("%d %d\n", array_edge_cases_g2[1][2], g3[1][0][1]);
    printf("%s %d\n", array_edge_cases_gs, sizeof(array_edge_cases_gs));
    for (i = 0; i < 5; i++) printf("%d ", part[i]);
    printf("\n");
    int cube[2][3][4]; int c = 0;
    for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) for (k = 0; k < 4; k++) cube[i][j][k] = c++;
    printf("%d %d\n", cube[1][2][3], cube[1][0][0]);
    printf("%d\n", sizeof(cube) / sizeof(int));
    printf("%d\n", sumrow(part, 5));
    char name[10] = "abc";
    name[3] = 'd'; name[4] = 0;
    printf("%s %d\n", name, name[7]);
    int idx = 1; int arr[4] = {5, 6, 7, 8};
    printf("%d %d\n", arr[idx + 1], arr[arr[0] - 4]);
    char cc[3] = {'x', 'y', 'z'}; cc[1] = cc[1] + 1; printf("%c%c%c\n", cc[0], cc[1], cc[2]);
    return 0;
}

/* ---- part: array_initializers (initialiser lists, inferred sizes, sizeof on arrays) ---- */
int tbl[] = {10, 20, 30, 40};
char name[8] = "abc";
int array_initializers_main(void) {
    int p[5] = {1, 2};
    int q[] = {7, 8, 9};
    int r[2][3] = {{1}, {2, 3}};
    int z[3] = {0};
    char s[] = "hey";
    printf("%d %d %d\n", p[0], p[1], p[4]);
    printf("%d %d\n", sizeof(q), sizeof(q) / sizeof(q[0]));
    printf("%d %d %d\n", r[0][0], r[0][2], r[1][2]);
    printf("%d %d\n", z[0], z[2]);
    printf("%d %d %d\n", sizeof(tbl), sizeof(s), sizeof(r));
    printf("%d %d %d\n", tbl[3], name[2], name[5]);
    int i = 0, sum = 0;
    while (i < sizeof(tbl) / sizeof(int)) sum += tbl[i++];
    printf("%d\n", sum);
    return 0;
}

/* ---- part: arrays_1d_2d_3d (1-D, 2-D and 3-D int arrays, global and local) ---- */
int arrays_1d_2d_3d_g1[5] = {5, 4, 3};
int arrays_1d_2d_3d_g2[2][3] = {{1, 2, 3}, {4, 5, 6}};
float arrays_1d_2d_3d_gf[3] = {1.5, 2};
int arrays_1d_2d_3d_main(void) {
    int a[6], i, j, k, s = 0;
    int m[3][4];
    int c[2][3][4];
    for (i = 0; i < 6; i++) a[i] = i * i;
    for (i = 0; i < 6; i++) s += a[i];
    printf("%d\n", s);
    for (i = 0; i < 3; i++) for (j = 0; j < 4; j++) m[i][j] = i * 10 + j;
    m[2][3] += 100; m[1][1]++; --m[0][2];
    for (i = 0; i < 3; i++) { for (j = 0; j < 4; j++) printf("%d ", m[i][j]); printf("\n"); }
    for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) for (k = 0; k < 4; k++) c[i][j][k] = i * 100 + j * 10 + k;
    printf("%d %d %d\n", c[1][2][3], c[0][1][2], c[1][0][0]);
    printf("%d %d %d\n", arrays_1d_2d_3d_g1[0], arrays_1d_2d_3d_g1[2], arrays_1d_2d_3d_g1[4]);
    printf("%d %d\n", arrays_1d_2d_3d_g2[0][2], arrays_1d_2d_3d_g2[1][0]);
    printf("%f %f %f\n", arrays_1d_2d_3d_gf[0], arrays_1d_2d_3d_gf[1], arrays_1d_2d_3d_gf[2]);
    i = 2;
    a[i++] += 7; printf("%d %d\n", a[2], i);
    printf("%d %d\n", a[i--], i);
    printf("%d\n", a[a[1] + 1]);
    float f[3];
    f[0] = 1; f[1] = f[0] / 4; f[2] = a[3] + f[1];
    printf("%f %f %f\n", f[0], f[1], f[2]);
    int x = (a[1] = 9) + 1;
    printf("%d %d\n", x, a[1]);
    return 0;
}

/* ---- part: char_arrays (char arrays and string initialisers) ---- */
char msg[] = "global";
int char_arrays_main(void) {
    char s[10] = "hello";
    char t[6];
    char *p = "world";
    int i, n = 0;
    printf("%s %s\n", s, msg);
    s[0] = 'H'; s[5] = '!'; s[6] = 0;
    printf("%s\n", s);
    for (i = 0; s[i] != 0; i++) n++;
    printf("%d\n", n);
    for (i = 0; i < 5; i++) t[i] = p[4 - i];
    t[5] = '\0';
    printf("%s %c %c\n", t, p[0], "xyz"[1]);
    for (i = 0; i < 5; i++) t[i] = t[i] - 32;
    printf("%s\n", t);
    t[0] = 200;
    printf("%d\n", t[0]);
    char grid[2][3] = {{'a', 'b', 'c'}, {'d', 'e', 'f'}};
    printf("%c%c\n", grid[0][2], grid[1][0]);
    return 0;
}

/* ---- part: edge_arrays ---- */
int edge_arrays_g1[3] = {1,2};
int edge_arrays_g2[2][2] = {{1,2},{3,4}};
char edge_arrays_gs[6] = "hello";
float edge_arrays_gf[2] = {1.5, 2.5};
void fill(int a[], int n) { int i; for (i = 0; i < n; i++) a[i] = i * i; }
int sum2(int m[][3], int r) { int s = 0, i, j; for (i = 0; i < r; i++) for (j = 0; j < 3; j++) s += m[i][j]; return s; }
void up(char s[]) { int i = 0; while (s[i] != 0) { if (s[i] >= 'a' && s[i] <= 'z') s[i] = s[i] - 32; i++; } }
int edge_arrays_main() {
    int a[1] = {7}; printf("%d\n", a[0]);
    int b[5] = {1,2}; printf("%d %d %d\n", b[0], b[1], b[4]);
    int c[2][3] = {{1,2,3},{4}}; printf("%d %d %d\n", c[0][2], c[1][0], c[1][2]);
    int d[2][2][2] = {{{1,2},{3,4}},{{5,6},{7,8}}}; printf("%d\n", d[1][0][1]);
    int e[] = {1,2,3,4}; printf("%d\n", (int)sizeof(e));
    printf("%d\n", (int)(sizeof(e) / sizeof(e[0])));
    char s[] = "abc"; printf("%d %s\n", (int)sizeof(s), s);
    char t[10] = "xy"; printf("%s %d\n", t, t[5]);
    char u[3] = {'a','b','c'}; printf("%c%c%c\n", u[0], u[1], u[2]);
    fill(b, 5); printf("%d\n", b[4]);
    printf("%d\n", sum2(c, 2));
    up(t); printf("%s\n", t);
    printf("%d %d %d\n", edge_arrays_g1[0], edge_arrays_g1[2], edge_arrays_g2[1][1]);
    printf("%s %f\n", edge_arrays_gs, edge_arrays_gf[1]);
    int i = 1; printf("%d\n", b[i + 1] * b[i]);
    int idx[3] = {2,1,0}; printf("%d\n", b[idx[0]]);
    b[b[1]] = 99; printf("%d\n", b[1]);
    char c2 = 'a'; int cnt[26] = {0}; cnt[c2 - 'a']++; cnt['c' - 'a'] += 2; printf("%d %d\n", cnt[0], cnt[2]);
    float fa[3]; fa[0] = 1; fa[1] = fa[0] / 4; printf("%f\n", fa[1]);
    int m2[3][3]; int p, q; for (p = 0; p < 3; p++) for (q = 0; q < 3; q++) m2[p][q] = p * 3 + q; printf("%d\n", m2[2][1]);
    return 0;
}

int main(void) {
    printf("== array_edge_cases\n");
    array_edge_cases_main();
    printf("== array_initializers\n");
    array_initializers_main();
    printf("== arrays_1d_2d_3d\n");
    arrays_1d_2d_3d_main();
    printf("== char_arrays\n");
    char_arrays_main();
    printf("== edge_arrays\n");
    edge_arrays_main();
    return 0;
}
