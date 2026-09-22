// Invalid: '[' without matching ']' before the operand of delete.
int main() {
    int *p = new int;
    delete[ p;
    return 0;
}
