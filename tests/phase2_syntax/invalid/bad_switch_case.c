// Covers: case label missing its colon
int main() {
    int n;
    switch (n) {
        case 1
            n = 1;
            break;
    }
    return 0;
}
