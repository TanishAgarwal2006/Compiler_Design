/* Lexical analysis: function, dynamic-memory and file-I/O words (printf scanf malloc free calloc realloc FILE fopen fclose fread fwrite ...)
   (several small programs joined into one file; each part is separated by a comment line) */

/* ---------- part: test4_functions_advanced.c ---------- */
typedef int MyInt;

int add(int a, int b) {
    return a + b;
}

int sum(int count, ...) {
    int total = 0;
    return total;
}

void increment(int &value) {
    value = value + 1;
}

int main(int argc, char **argv) {
    MyInt x = 5;
    MyInt y = 10;
    int z = add(x, y);

    int total = sum(3, 1, 2, 3);

    int *heap = (int *) malloc(10 * sizeof(int));
    heap[0] = 42;
    free(heap);

    increment(z);

    if (argc > 1) {
        printf("%s\n", argv[1]);
    }

    return 0;
}

/* ---------- part: test8_file_manipulation.c ---------- */
/* Covers this language's custom file_keyword reserved words: FILE,
 * fopen, fclose, fread, fwrite, fprintf, fscanf, fgets, fputs, feof.
 * Real C treats all of these as ordinary <stdio.h> library identifiers;
 * here they are reserved keywords by design (see lexer.l header).
 */

int main() {
    FILE *fp;
    char buffer[100];
    int value;

    fp = fopen("data.txt", "r");
    if (fp) {
        fgets(buffer, 100, fp);
        fscanf(fp, "%d", &value);
        while (!feof(fp)) {
            fread(buffer, 1, 100, fp);
        }
        fclose(fp);
    }

    fp = fopen("out.txt", "w");
    fputs("hello", fp);
    fprintf(fp, "%d\n", value);
    fwrite(buffer, 1, 100, fp);
    fclose(fp);

    return 0;
}
