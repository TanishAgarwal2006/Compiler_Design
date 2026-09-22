// Covers: if/else (incl. dangling else), for (incl. a declaration in the
// init slot), while, do-while, switch/case/default (incl. an empty body),
// break/continue, and goto with labels
int classify(int n) {
    if (n > 0) {
        return 1;
    } else if (n < 0) {
        return -1;
    } else {
        return 0;
    }
}

int classify_switch(int n) {
    int result;
    switch (n) {
        case 1:
            result = 10;
            break;
        case 2:
        case 3:
            result = 20;
            break;
        default:
            result = -1;
    }
    return result;
}

int main() {
    int r = classify(-5);
    printf("%d\n", r);

    // dangling else: must attach to the inner 'if (b == 2)'
    int a = 1, b = 2, c = 3;
    if (a == 1)
        if (b == 2)
            c = 10;
        else
            c = 20;

    int i, sum = 0;
    for (i = 0; i < 10; i++) {
        if (i == 3) {
            continue;
        }
        if (i == 7) {
            break;
        }
        sum += i;
    }
    for (;;) {
        break;
    }
    for (int j = 0; j < 3; j++) {
        sum += j;
    }

    switch (a) {
    }

    i = 0;
    while (i < 10) {
        sum += i;
        i++;
    }
    while (b < 5)
        b++;
    while (b < 10); // semicolon-only body

    i = 0;
    do {
        printf("%d\n", i);
        i++;
    } while (i < 5);

    printf("%d\n", classify_switch(2));

    i = 0;
loop_start:
    if (i >= 5) {
        goto loop_end;
    }
    printf("%d\n", i);
    i++;
    goto loop_start;
loop_end:
    return 0;
}
