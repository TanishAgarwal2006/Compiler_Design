int main()
{
    int x;
    char c;


    x = 10;


    // Illegal characters
    x = 20 @ 30;

    x = 50 $ 10;

    x = 5 # 2;


    // Invalid identifier characters
    int 123abc;


    // Unterminated string
    printf("Hello World);


    // Unterminated character
    c = 'A;


    // Invalid escape sequence
    c = '\z';


    // Empty character constant
    c = '';


    // Multi-character constant
    c = 'ab';


    // Unsupported symbols
    x = 10 ^ 2;

    x = 5 | 3;


    // Unterminated multiline comment
    /*
       This comment never closes

    return 0;
}