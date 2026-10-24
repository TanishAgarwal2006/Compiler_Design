/* Lexical analysis: type keywords, qualifiers and storage classes (int char float double bool short long signed unsigned const volatile static auto typedef enum)
   (several small programs joined into one file; each part is separated by a comment line) */

/* ---------- part: test7_type_modifiers_and_custom_keywords.c ---------- */
/* Covers:
 *  - size/sign type modifiers: short, long, long long, signed, unsigned
 *  - this language's custom reserved keywords that real C treats as
 *    ordinary library identifiers: printf, scanf, malloc, free, calloc,
 *    realloc
 *  - numeric literal forms: hex (0x1F), octal (017), binary (0b1101),
 *    integer suffixes (U, L, LL and their combinations), float suffix
 *    (f), and leading/trailing-dot floats (.5, 5.)
 *  - boolean literals: true, false
 */

int main() {
    short s = 5;
    long l = 100000;
    long long ll = 10000000000;
    signed int si = -3;
    unsigned int ui = 3;
    unsigned long ul = 4000000000;
    double d = 2.5;

    int hex = 0x1F;
    int oct = 017;
    int bin = 0b1101;
    unsigned int u1 = 45U;
    unsigned int u2 = 45u;
    long l1 = 45L;
    unsigned long ul1 = 45UL;
    long long ll1 = 45LL;
    unsigned long long ull1 = 45ULL;
    unsigned long long ull2 = 45LLU;
    float f = 3.14f;
    float leading_dot = .5;
    float trailing_dot = 5.;

    int flag_true = true;
    int flag_false = false;

    int *heap = (int *) malloc(10 * sizeof(int));
    int *more = (int *) calloc(5, sizeof(int));
    more = (int *) realloc(more, 10 * sizeof(int));
    heap[0] = 42;
    free(heap);
    free(more);

    printf("%d %d\n", si, ui);
    scanf("%d", &si);

    return 0;
}

/* ---------- part: test3_arrays_pointers_structs.c ---------- */
struct Point {
    int x;
    int y;
};

enum Color {
    RED,
    GREEN,
    BLUE
};

union Data {
    int i;
    float f;
    char str[20];
};

typedef struct Point Point2D;

int main() {
    int nums[10];
    char letters[26];
    int grid[4][4];
    int cube[2][2][2];

    int *p;
    int **pp;
    int ***ppp;

    struct Point origin;
    struct Point *ptr;
    enum Color favorite;
    union Data data;

    nums[0] = 1;
    letters[0] = 'a';
    grid[1][2] = 5;
    cube[0][1][1] = 9;

    p = &nums[0];
    pp = &p;
    ppp = &pp;

    origin.x = 0;
    origin.y = 0;
    ptr = &origin;
    ptr->x = 3;
    ptr->y = 4;

    favorite = GREEN;
    data.i = 5;

    printf("%d %d\n", ptr->x, ptr->y);
    scanf("%d", &nums[1]);

    return 0;
}

/* ---------- part: volatile_and__Bool ---------- */
/* Covers the last two keywords: the qualifier 'volatile' and C99's spelling '_Bool' of 'bool'. */
volatile int vol_counter = 0;
_Bool flag_c99 = 1;
const volatile int vol_const = 7;
