int main() {
    int a = 1, b = 2, c = 3, d = 4;
    int res;

    // 1. Right associativity of assignment
    a = b = c = d + 5; 

    // 2. Mixed precedence: arithmetic -> relational -> logical
    res = a + b * c == d - 1 && c < d || !a;

    // 3. Unary operators
    res = -a + +b - --c;

    // 4. Compound assignment precedence
    a += b *= c -= 1;

    return 0;
}