// Feature: Control Flow
// One file covering every small program of this feature, run in order by main().
#include <stdio.h>
#include <stdlib.h>

/* ---- part: all_statements (if, for, while, do-while, switch, goto, break, continue, ternary together) ---- */
int all_statements_main(void) {
    int i, n = 0, total = 0;
    for (i = 0; i < 10; i++) {
        if (i % 2 == 0) continue;
        if (i > 7) break;
        total += i;
    }
    while (n < 3) { n++; }
    do { n--; } while (n > 0);
    switch (total) {
        case 1: printf("one\n");
        case 16: printf("sixteen\n");
        case 17: printf("seventeen\n"); break;
        default: printf("other\n");
    }
    i = 0;
loop:
    i++;
    if (i < 3) goto loop;
    printf("%d %d %d\n", total, n, i);
    printf("%d\n", (total > 5 && i == 3) ? 1 : 0);
    printf("%d\n", (total < 0 || !n));
    return 0;
}

/* ---- part: break_continue (break and continue in nested loops) ---- */
int break_continue_main(void) {
    int i, j, n = 0;
    for (i = 0; i < 5; i++) {
        if (i == 1) continue;
        for (j = 0; j < 5; j++) {
            if (j == 3) break;
            if (j == 1) continue;
            n += i * 10 + j;
            printf("%d ", i * 10 + j);
        }
        if (i == 3) break;
    }
    printf("\nn=%d\n", n);
    i = 0;
    while (1) { i++; if (i > 6) break; if (i % 2) continue; printf("w%d ", i); }
    do { i--; if (i == 4) continue; printf("d%d ", i); } while (i > 2);
    for (;;) { i += 5; if (i > 20) break; }
    printf("\ni=%d\n", i);
    return 0;
}

/* ---- part: for_declaration (for with a declaration in the init part) ---- */
int for_declaration_main(void) {
    int total = 0;
    for (int i = 0; i < 4; i++) {
        for (int j = i; j < 4; j++) total += i * j;
    }
    printf("%d\n", total);
    for (int i = 10; i > 7; i--) printf("%d ", i);
    printf("\n");
    int i = 99;
    for (int i = 0; i < 2; i++) { int i2 = i * 3; printf("%d ", i2); }
    printf("%d\n", i);
    for (;;) { total++; if (total > 30) break; }
    printf("%d\n", total);
    return 0;
}

/* ---- part: goto_loops (goto and labels used as loops) ---- */
int goto_loops_main(void) {
    int i = 0, sum = 0;
top:
    if (i >= 5) goto done;
    sum += i;
    i++;
    goto top;
done:
    printf("sum=%d\n", sum);
    for (i = 0; i < 3; i++) {
        int j = 0;
inner:
        if (j == 2) continue;
        j++;
        printf("%d%d ", i, j);
        goto inner;
    }
    printf("\n");
    goto end;
    printf("skipped\n");
end:
    ;
    return 0;
}

/* ---- part: goto_out_of_loops (goto out of nested loops) ---- */
int goto_out_of_loops_main(void) {
    int i, j, found = 0;
    for (i = 0; i < 5; i++)
        for (j = 0; j < 5; j++)
            if (i * j == 6) { found = i * 10 + j; goto done; }
done:
    printf("%d\n", found);
    i = 0;
top:
    if (i >= 3) goto end;
    printf("i=%d\n", i);
    i++;
    goto top;
end:
    printf("end\n");
    return 0;
}

/* ---- part: if_else (if, else if chains, dangling else) ---- */
int if_else_main(void) {
    int i;
    for (i = -1; i < 4; i++) {
        if (i < 0) printf("neg\n");
        else if (i == 0) printf("zero\n");
        else if (i == 1) { printf("one\n"); }
        else if (i < 3) printf("small\n");
        else ;
        if (i) if (i > 2) printf("big\n"); else printf("notbig\n");
    }
    return 0;
}

/* ---- part: switch_edge_cases (switch on char, default first, empty cases) ---- */
int classify(char c) {
    switch (c) {
        case 'a': case 'e': case 'i': case 'o': case 'u': return 1;
        default: return 0;
        case ' ': return 2;
    }
}
int switch_edge_cases_main(void) {
    int i, n = 0;
    for (i = 0; i < 12; i++) {
        switch (i % 4) {
            case 0: n += 1;
            case 1: n += 10; break;
            case 2: continue;
            default: n += 100;
        }
        n += 1000;
    }
    printf("%d\n", n);
    printf("%d %d %d\n", classify('e'), classify('z'), classify(' '));
    int k = 5;
    switch (k) { case 1: printf("one\n"); }
    switch (k) { }
    switch (k) { case 5: { int t = 9; printf("t=%d\n", t); } break; case 6: break; }
    switch (k) {
        case 5:
            switch (k + 1) { case 6: printf("inner\n"); break; default: printf("no\n"); }
            printf("after inner\n");
            break;
    }
    switch (-3) { case -3: printf("neg\n"); break; }
    return 0;
}

/* ---- part: switch_fallthrough (switch, case fall-through, default, break) ---- */
int switch_fallthrough_main(void) {
    int i;
    for (i = 0; i < 7; i++) {
        switch (i) {
            case 0: printf("zero ");
            case 1: printf("one "); break;
            case 2: { printf("two "); }
            default: printf("dflt ");
            case 4: printf("four "); break;
            case 5: continue;
        }
        printf("| ");
    }
    printf("\n");
    char c = 'b';
    switch (c) { case 'a': printf("A\n"); break; case 'b': printf("B\n"); case 'c': printf("C\n"); }
    switch (i) { case 100: printf("no\n"); }
    switch (3) { case 3: printf("const\n"); break; }
    i = 1;
    switch (i) { case 1: i = 2; case 2: printf("i=%d\n", i); }
    return 0;
}

/* ---- part: ternary (?: operator, nested and as an operand) ---- */
int ternary_main(void) {
    int a = 3, b = 8, m;
    m = a > b ? a : b;
    printf("%d\n", m);
    float f = a < b ? 1 : 2.5;
    printf("%f\n", f);
    char c = a ? 'y' : 'n';
    printf("%c\n", c);
    printf("%d\n", a ? b ? 1 : 2 : 3);
    printf("%s\n", a > 5 ? "big" : "small");
    a = 0;
    m = (a++ || b) ? a : -a;
    printf("%d %d\n", m, a);
    return 0;
}

/* ---- part: edge_control ---- */
int edge_control_main() {
    int i;
    for (;;) { i++; if (i > 3) break; } printf("%d\n", i);
    for (i = 0; i < 3; i++) ; printf("%d\n", i);
    int j = 0; for (; j < 5;) j += 2; printf("%d\n", j);
    for (int k = 0, q = 10; k < q; k += 3, q--) printf("%d,%d ", k, q); printf("\n");
    i = 0; do { i++; if (i == 2) continue; printf("%d ", i); } while (i < 4); printf("\n");
    i = 0; while (i < 10) { i++; if (i % 2) continue; if (i > 6) break; printf("%d ", i); } printf("\n");
    for (i = 0; i < 3; i++) for (j = 0; j < 3; j++) { if (j == 1) continue; if (i == 2) break; printf("%d%d ", i, j); } printf("\n");
    switch (2) { case 1: printf("one\n"); case 2: printf("two\n"); case 3: printf("three\n"); break; default: printf("def\n"); }
    switch (9) { default: printf("d\n"); case 1: printf("one\n"); }
    switch (1) { case 1: { int v = 5; printf("%d\n", v); } break; case 2: break; }
    for (i = 0; i < 4; i++) { switch (i) { case 1: continue; case 2: break; default: printf("x%d ", i); } printf("y%d ", i); } printf("\n");
    switch ('a') { case 'a': printf("A\n"); break; case 'b': printf("B\n"); }
    int sw = 3; switch (sw) { }
    switch (sw) { case 1+2: printf("three\n"); break; }
    i = 0; goto skip; i = 100; skip: printf("%d\n", i);
    i = 0; back: i++; if (i < 3) goto back; printf("%d\n", i);
    if (i == 3) if (j == 100) printf("a\n"); else printf("b\n");
    if (0) ; else printf("else\n");
    { { { printf("deep\n"); } } }
    return 0;
}

/* ---- part: edge_nested ---- */
int grid[3][4];
int cnt;
int next() { return ++cnt; }
int sq(int x) { return x * x; }
int edge_nested_main() {
    int i, j;
    for (i = 0; i < 3; i++) for (j = 0; j < 4; j++) grid[i][j] = next();
    int total = 0;
    for (i = 0; i < 3; i++) { int rowsum = 0; for (j = 0; j < 4; j++) rowsum += grid[i][j]; printf("%d ", rowsum); total += rowsum; }
    printf("\n%d\n", total);
    int a = 5, b = 10;
    printf("%d\n", a < b && b < 20 || a > 100);
    printf("%d\n", (a > b) ? a : b);
    printf("%d\n", sq(sq(2)) + sq(3));
    printf("%d\n", a && (b = 0));
    printf("%d\n", b);
    int z = 0; if (z++ || z++) printf("z=%d\n", z);
    int w = 1; if (w-- && w--) printf("no\n"); printf("w=%d\n", w);
    int k = 10; while (k --> 7) printf("%d ", k); printf("\n");
    int m = 0; m += m++ + 1; 
    int fa = 3; int fb = fa > 2 ? (fa < 5 ? 1 : 2) : 3; printf("%d\n", fb);
    char c = 'x'; printf("%d\n", c == 'x' ? 1 : 0);
    printf("%d\n", ((((1 + 2) * 3) - 4) / 5));
    return 0;
}

int main(void) {
    printf("== all_statements\n");
    all_statements_main();
    printf("== break_continue\n");
    break_continue_main();
    printf("== for_declaration\n");
    for_declaration_main();
    printf("== goto_loops\n");
    goto_loops_main();
    printf("== goto_out_of_loops\n");
    goto_out_of_loops_main();
    printf("== if_else\n");
    if_else_main();
    printf("== switch_edge_cases\n");
    switch_edge_cases_main();
    printf("== switch_fallthrough\n");
    switch_fallthrough_main();
    printf("== ternary\n");
    ternary_main();
    printf("== edge_control\n");
    edge_control_main();
    printf("== edge_nested\n");
    edge_nested_main();
    return 0;
}
