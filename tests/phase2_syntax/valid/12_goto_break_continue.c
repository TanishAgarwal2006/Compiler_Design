int main() {
    int i;
    for (i = 0; i < 10; i++) {
        if (i == 3) {
            continue;
        }
        if (i == 7) {
            break;
        }
        printf("%d\n", i);
    }

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
