/* "Command line input" - values supplied to the running program via
   scanf, read into variables and arrays for further processing. */
int main() {
    int n, i;
    int values[10];
    printf("How many values? ");
    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%d", &values[i]);
    }
    return 0;
}
