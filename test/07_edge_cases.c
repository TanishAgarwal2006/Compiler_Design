int main()
{
    // Single line comment test

    /*
       Multi-line comment test
       Lexer should ignore this completely
    */


    int _counter123;
    char _letter;


    _counter123 = 100;

    _letter = 'A';


    // Escape character tests
    char newline;
    char quote;

    newline = '\n';
    quote = '\'';


    // String literal tests
    printf("Hello World");

    printf("Line1\nLine2");


    // Empty statement
    ;


    // Nested blocks
    {
        {
            _counter123++;
        }
    }


    // Multiple operators together
    _counter123 += 5;
    _counter123 -= 2;

    if((_counter123 >= 10) && (_counter123 != 0))
    {
        _counter123 = _counter123 + 1;
    }


    // Identifier edge cases
    int variable123;
    int _;


    variable123 = 50;
    _ = variable123;


    return 0;
}