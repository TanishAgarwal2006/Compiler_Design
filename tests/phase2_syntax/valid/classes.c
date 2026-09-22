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
