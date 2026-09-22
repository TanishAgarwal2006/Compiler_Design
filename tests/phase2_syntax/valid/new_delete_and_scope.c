// Covers: free-store allocation (new/delete, including array form) and
// scope-resolved (::) access to a base class member.
class Base {
public:
    int value;
    int getValue() { return value; }
};

class Derived : public Base {
public:
    int getBaseValue() { return Base::value; }
};

int main() {
    int *p = new int;
    *p = 42;
    delete p;

    int *arr = new int[10];
    arr[0] = 1;
    delete[] arr;

    Derived d;
    d.value = 7;
    int v = d.getBaseValue();

    int w = Derived::value;

    return 0;
}
