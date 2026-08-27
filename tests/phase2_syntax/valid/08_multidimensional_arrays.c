int main() {
    int matrix[2][3];
    int cube[2][2][2];
    int i, j;
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 3; j++) {
            matrix[i][j] = i + j;
        }
    }
    cube[0][1][1] = 7;
    return 0;
}
