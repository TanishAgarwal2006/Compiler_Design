int main()
{
    int x;

    x = 10;


    // Normal if else
    if(x > 5)
    {
        x = 20;
    }
    else
    {
        x = 30;
    }


    // Dangling else case
    if(x > 0)
        if(x > 5)
            x = 50;
        else
            x = 100;


label:

    x++;

    if(x > 100)
    {
        goto end;
    }


end:

    return 0;
}