// Covers: arithmetic/relational/logical operators, unary operators, and
// operator precedence/associativity
int main() {
    int a = 12, b = 5, r;
    r = a + b;
    r = a - b;
    r = a * b;
    r = a / b;
    r = a % b;
    r = (a > b) && (a != 0);
    r = (a < b) || (b == 5);
    r = !r;

    int c = 3, d = 4;

    // right associativity of assignment
    a = b = c = d + 5;

    // mixed precedence: arithmetic -> relational -> logical
    r = a + b * c == d - 1 && c < d || !a;

    // unary operators
    r = -a + +b - --c;

    // compound assignment precedence
    a += b *= c -= 1;

    return 0;
}
