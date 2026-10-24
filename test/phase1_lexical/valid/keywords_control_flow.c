/* Lexical analysis: control-flow and loop keywords (if else for while do until switch case default break continue goto return)
   (several small programs joined into one file; each part is separated by a comment line) */

/* ---------- part: test2_control_flow.c ---------- */
static int counter;

int classify(int n) {
    switch (n) {
        case 0:
            return 0;
        case 1:
            return 1;
        default:
            break;
    }

    for (counter = 0; counter < n; counter++) {
        if (counter == 5) {
            continue;
        }
        if (counter == 8) {
            break;
        }
    }

    while (counter > 0) {
        counter--;
    }

    do {
        counter++;
    } while (counter < n);

    counter = 0;
    until (counter >= n) {
        counter++;
        if (counter == 100) {
            goto done;
        }
    }

done:
    return counter;
}

/* ---------- part: test5_until_loop.c ---------- */
int main() {
    int i = 0;
    float pi = 3.14159f;
    float small = 1.5e-3;
    int mask = 0x1F;
    char newline = '\n';
    char *msg = "hello, world\n";

    until (i >= 5) {
        i = i + 1;
    }

    return 0;
}
