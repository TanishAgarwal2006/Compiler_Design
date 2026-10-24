// Lexical errors in preprocessor lines and comments.
#includ <stdio.h>     // 1: unknown directive
#                     // 2: a lone '#' is a stray '#'
int main() {
    return 0;
}
/* 3: this comment is never closed, so it swallows the rest of the file
int after = 1;
