/* Arithmetic operators: + - * / % and compound assignments */
int main() {
    int a = 10, b = 3, c;
    c = a + b;
    c = a - b;
    c = a * b;
    c = a / b;
    c = a % b;
    a += 1;
    a -= 1;
    a *= 2;
    a /= 2;
    a %= 2;
    a++;
    a--;
    ++a;
    --a;
    return 0;
}
