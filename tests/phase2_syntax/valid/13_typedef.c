typedef int Integer;
typedef char Letter;

Integer square(Integer x) {
    return x * x;
}

int main() {
    Integer n = 5;
    Letter grade = 'A';
    printf("%d\n", square(n));
    return 0;
}
