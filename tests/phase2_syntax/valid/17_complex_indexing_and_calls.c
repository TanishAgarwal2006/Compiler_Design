int compute_index(int x) {
    if (x <= 1) return x;
    return compute_index(x - 1) + compute_index(x - 2);
}

int main(int argc, char argv[][]) {
    int matrix[10][10];
    int i = 2;
    int j = 3;

    matrix[i + 1][j * 2 - 1] = 42;

    matrix[compute_index(5)][compute_index(3)] = 100;

    printf("Computed Value: %d\n", compute_index(matrix[0][0]));
    
    scanf("%d", &matrix[i][j]);

    return 0;
}