/* Syntax errors in statements and expressions: missing semicolons, bad call
   arguments, unbalanced parentheses, malformed delete. One function per case;
   each case is marked [n] and must give exactly one error. */

void resync_marker() {}

/* [1] missing ';' after an expression statement */
int s01_missing_semicolon_expr(int a) {
    a = a + 1
    return a;
}

/* [2] missing ';' after a declaration */
int s02_missing_semicolon_decl(void) {
    int x = 1
    return x;
}

/* [4] call with a trailing comma in the argument list */
int f(int a, int b) { return a + b; }
int s04_call_trailing_comma(void) {
    return f(1, );
}

/* [5] call with two commas in a row */
int s05_call_double_comma(void) {
    return f(1,, 2);
}

/* [6] call whose argument list is never closed */
int s06_call_unclosed(void) {
    return f(1, 2;
}

/* [7] extra ')' in an expression */
int s07_extra_close_paren(int a) {
    return (a + 1));
}

/* [8] missing ')' in a parenthesised expression */
int s08_missing_close_paren(int a) {
    return (a + 1;
}

/* [9] empty parentheses used as an expression */
int s09_empty_parens(void) {
    int x = ();
    return x;
}

/* [10] operator with no right operand */
int s10_dangling_operator(int a) {
    return a + ;
}

/* [11] delete[ without the closing ']' */
void s11_delete_open_bracket(int *p) {
    delete[ p;
}

/* [12] delete[] with nothing to delete */
void s12_delete_nothing(void) {
    delete[];
}

/* [13] [boundary] fine on its own: delete[] with an expression */
void s13_delete_ok(int *p) {
    delete[] p;
}

/* [14] missing ';' after return */
int s14_missing_semicolon_return(int a) {
    return a + 1
}

