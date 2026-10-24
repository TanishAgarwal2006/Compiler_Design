// Lexical errors in character and string literals.
char ok1 = 'a';
char a = '';                  // 1: empty character constant
char b = 'AB';                // 2: more than one character
char c = '\q';                // 3: unknown escape in a character
char d = 'a;                  // 4: character not closed
char *e = "oops;              // 5: string not closed
char *f = "bad \xz escape";   // 6: \x without hex digits
char *g = "bad \89 escape";   // 7: \8 is not an escape
char *h = "bad \q escape";    // 8: unknown escape in a string
char ok2 = 'b';
char i = '\n\n';              // 9: two escapes in one character
char j = 'é';                 // 10: non-ASCII character
