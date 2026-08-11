int factorial(int n)
{
    if(n <= 1)
    {
        return 1;
    }

    return n * factorial(n-1);
}



int add(int a, int b)
{
    return a+b;
}



int main()
{
    int result;

    result = add(5,10);

    result = factorial(5);
    int x = factorial(5) + add(2,3);
    return 0;
}