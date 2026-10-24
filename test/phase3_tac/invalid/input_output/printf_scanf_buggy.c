// Feature: printf / scanf / atoi misuse (deliberately wrong)
// Every function holds one mistake; the .err file lists the message each one must produce.

int bug_printf_without_format(void) { printf(); return 0; }
int bug_printf_lone_percent(void) { printf("100%"); return 0; }
int bug_scanf_literal_text(void) { scanf("a"); return 0; }
int bug_scanf_s_on_pointer(void) { char *p; scanf("%s", p); return 0; }
int bug_scanf_s_on_int_array(void) { int a[3]; scanf("%s", a); return 0; }
int bug_atoi_no_argument(void) { return atoi(); }
int bug_atoi_int_argument(void) { return atoi(5); }

int main(void) { return 0; }
