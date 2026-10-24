// Lexical errors: characters that are not part of the language.
int main() {
    int a = 5 @ 3;          // 1: @
    int b = a $ 2;          // 2: $
    int c = `a`;            // 3: backquote
    int d = a \ 2;          // 4: backslash outside a literal
    return 0;
}
