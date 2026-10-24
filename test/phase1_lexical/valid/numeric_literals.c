/* Lexical analysis: every kind of number the lexer accepts. */
int decimal = 0, d1 = 7, d2 = 1234567890;
int hex_lower = 0xff, hex_upper = 0XFF, hex_mixed = 0xDeadBeef;
int binary = 0b1011, binary_upper = 0B11;
int octal = 017, octal_zero_zero = 00, octal_big = 0777;
/* integer suffixes u l ul lu ll ull (any case) are accepted and ignored */
int s1 = 45U, s2 = 45u, s3 = 45L, s4 = 45l, s5 = 45UL, s6 = 45ul, s7 = 45LU, s8 = 45LL, s9 = 45ULL, s10 = 0x1FUL;
/* floating point: plain, leading dot, trailing dot, exponent, suffix f / l */
float f1 = 3.14, f2 = .5, f3 = 5., f4 = 1e3, f5 = 2.5e-1, f6 = 1E+2, f7 = 1.5f, f8 = 2.0F, f9 = 3e2f, f10 = 0.0;
int a = 1+2, b = 3-4, c = 5*6;       /* digits next to operators */
int main() { return 0; }
