/* Syntax analysis: classes, access labels, constructors, destructors, out-of-class methods, this
   (several small programs joined into one file; each part is marked by a comment line) */

/* ---------- part: classes.c ---------- */
// Covers: class definitions, inheritance, and public/private/protected
// access labels with member functions
class Animal {
public:
    int age;
    int getAge() { return age; }
protected:
    int legs;
private:
    char name[20];
};

class Dog : public Animal {
public:
    int bark() { return legs + 1; }
};

int main() {
    Dog d;
    d.age = 3;
    return d.bark();
}

/* ---------- part: test13_this_valid_usage.c ---------- */


class Dog {
public:
    int legs;
    int bark() {
        return this->legs;
    }
    int legCount();
};

int Dog::legCount() {
    return this->legs;
}

int main() {
    return 0;
}

/* ---------- part: test7_cpp_features.c ---------- */


class Animal {
public:
    int legs;
};

class Dog : public Animal {
public:
    Dog(int n) {
        legs = n;
    }
    ~Dog() {
    }
    int bark() {
        return legs;
    }
};

int main() {
    bool flag;
    flag = true;
    const int limit = 10;

    int *p;
    p = new int;
    delete p;

    int arr[5];
    int sz;
    sz = sizeof(arr);
    int sz2;
    sz2 = sizeof(int);

    Dog d;          /* class name used directly, no `class` keyword needed */
    d.legs = 4;
    int legs;
    legs = d.bark();

    return 0;
}

/* ---------- part: test8_out_of_class_methods.c ---------- */


class Dog {
public:
    int legs;
    int bark();
};

int Dog::bark() {
    return legs;
}

int main() {
    Dog d;
    int b;
    b = d.bark();
    return 0;
}
