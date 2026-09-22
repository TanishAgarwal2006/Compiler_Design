// Covers: illegal character not part of the token set ('@')
int main() {
    int x = 5;
    x = x @ 2;
    return 0;
}
