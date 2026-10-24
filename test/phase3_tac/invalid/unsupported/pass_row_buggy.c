// Feature: a row of a 2-D array cannot be passed to a function (reported only when nothing else is wrong).
int row_taker(int r[2]) { return r[0]; }
int main(void) { int m[2][2] = {{1, 2}, {3, 4}}; return row_taker(m[1]); }
