/* Lexical analysis: class keywords (class public private protected this new delete ::) and lambdas ([] -> auto)
   (several small programs joined into one file; each part is separated by a comment line) */

/* ---------- part: test9_classes_and_objects.c ---------- */
/* Covers this language's object-oriented keywords/operators:
 *  - class
 *  - access modifiers: public, private, protected
 *  - this (self-reference inside a method)
 *  - :: (scope resolution)
 */

class Animal {
    public:
        int age;

        void setAge(int a) {
            this->age = a;
        }

        int getAge() {
            return this->age;
        }

        auto ageGetter() {
            return [this]() { return this->age; };
        }

    private:
        int secretId;

    protected:
        int sharedValue;
};

class Dog {
    public:
        Animal base;

        void bark() {
            this->base.age = 1;
        }
};

int main() {
    Animal a;
    a.setAge(5);

    Dog d;
    d.bark();

    Animal::setAge;

    return 0;
}

/* ---------- part: test10_lambda_functions.c ---------- */
/* Lambda functions use C++-style syntax: [capture](params) { body }
 * No new tokens were needed for this -- every piece decomposes into
 * tokens the lexer already had: [ ], ( ), { }, ->, and existing
 * operators/identifiers inside the capture list. The one real gap this
 * exposed was 'auto' not being a keyword -- fixed alongside this test,
 * since a lambda's value needs somewhere to be assigned.
 */

int main() {
    auto add = [](int x, int y) {
        return x + y;
    };

    auto byRef = [&](int x) {
        return x + 1;
    };

    auto byValue = [=](int x) {
        return x + 1;
    };

    int a = 1;
    int b = 2;
    auto mixedCapture = [a, &b](int z) {
        return a + b + z;
    };

    auto withReturnType = [](int x) -> int {
        return x * 2;
    };

    return 0;
}
