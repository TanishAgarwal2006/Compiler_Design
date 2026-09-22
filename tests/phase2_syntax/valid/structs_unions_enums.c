// Covers: struct definitions and pointer member access (.  and ->),
// enum (implicit and explicit values), union, and typedef
typedef int Integer;
typedef char Letter;

struct Point {
    int x;
    int y;
};

union Value {
    int i;
    char c;
};

enum Color { RED, GREEN, BLUE };
enum Status { OK = 0, FAIL = 1 };

Integer square(Integer x) {
    return x * x;
}

int main() {
    Integer n = 5;
    Letter grade = 'A';
    printf("%d\n", square(n));

    struct Point p1;
    struct Point *pp;
    p1.x = 3;
    p1.y = 4;
    pp = &p1;
    pp->x = 5;

    enum Color c = RED;
    enum Status s = FAIL;

    union Value v;
    v.i = 65;

    return v.i;
}
