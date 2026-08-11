int main()
{
    int i;

    i = 0;


    while(i < 10)
    {
        if(i == 5)
        {
            break;
        }

        i++;
    }


    do
    {
        i--;

        if(i == 2)
        {
            continue;
        }

    }while(i > 0);



    for(i = 0; i < 10; i++)
    {
        continue;
    }


    return 0;
}