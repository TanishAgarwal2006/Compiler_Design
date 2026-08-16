int main()
{
    int a;
    int b;
    int c;

    a = 10;
    b = 5;
    a = 0x123;

    c = a + b;
    c = a - b;
    c = a * b;
    c = a / b;
    c = a % b;

    c += 1;
    c -= 1;
    c *= 2;
    c /= 2;
    c %= 3;

    if(a > b && b < c)
    {
        c = c + 1;
    }

    if(a == b || a != c)
    {
        c = 0;
    }

    return 0;
}