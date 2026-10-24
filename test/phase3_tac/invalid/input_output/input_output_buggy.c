// Feature: Input Output (deliberately wrong)
// Every part below holds one mistake; the .err file lists the message each one must produce.


/* ---- bug: printf_arg_count -- printf format has 2 conversion(s) but 1 argument(s) ---- */
int bug_printf_arg_count(void) {
    printf("%d %d", 1);
    return 0;
}

/* ---- bug: printf_nonliteral_format -- must be a string literal ---- */
int bug_printf_nonliteral_format(void) {
    char s[4] = "ab";
    printf(s);
    return 0;
}

/* ---- bug: printf_type_mismatch -- printf %d cannot print a value of type float ---- */
int bug_printf_type_mismatch(void) {
    printf("%d", 1.5);
    return 0;
}

/* ---- bug: printf_unsupported_specifier -- unsupported format specifier '%.2f' ---- */
int bug_printf_unsupported_specifier(void) {
    printf("%.2f", 1.5);
    return 0;
}

/* ---- bug: scanf_missing_address -- needs the address of a variable ---- */
int bug_scanf_missing_address(void) {
    int x;
    scanf("%d", x);
    return 0;
}

/* ---- bug: scanf_no_args -- scanf format has 1 conversion(s) but 0 argument(s) ---- */
int bug_scanf_no_args(void) { int x; scanf("%d"); return 0; }

/* ---- bug: scanf_wrong_type -- scanf %d needs the address of a int variable ---- */
int bug_scanf_wrong_type(void) {
    float f;
    scanf("%d", &f);
    return 0;
}

int main(void) { return 0; }
