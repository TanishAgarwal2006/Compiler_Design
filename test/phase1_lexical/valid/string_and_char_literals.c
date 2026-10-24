/* Lexical analysis: string and character literals with every escape sequence. */
char plain = 'a', digit = '7', space = ' ', quote_in_char = '"', apos = '\'';
char e1 = '\n', e2 = '\t', e3 = '\r', e4 = '\b', e5 = '\f', e6 = '\v', e7 = '\a', e8 = '\0', e9 = '\\', e10 = '\?';
char oct = '\101', hex = '\x41', oct_short = '\7';
char *s1 = "hello world";
char *s2 = "";
char *s3 = "tab\there, newline\n, backslash\\, quote\", apostrophe\'";
char *s4 = "octal \101\102 hex \x41\x42 bell\a question\?";
char *s5 = "// not a comment";
char *s6 = "/* not a comment either */";
char *s7 = "'single quotes' inside";
char s8[] = "array initialiser";
char *joined = "a" "b";          /* two literals side by side: two tokens */
int main() { return 0; }
