/* Syntax analysis: lambdas, auto and references (accepted by the parser, rejected by phase 3). */
int global_counter = 0;

void by_reference(int &value) { value = value + 1; }
int &identity(int &v) { return v; }

int main() {
    auto add = [](int x, int y) { return x + y; };
    auto by_ref = [&](int x) { return x + 1; };
    auto by_value = [=](int x) { return x + 1; };
    int a = 1;
    int b = 2;
    auto mixed = [a, &b](int z) { return a + b + z; };
    auto with_type = [](int x) -> int { return x * 2; };
    auto no_params = [] { return 7; };
    auto capture_this = [this]() { return 1; };
    auto capture_all_but = [=, &b](int q) { return q + b; };
    auto nested = [](int n) { auto inner = [n](int m) { return n + m; }; return inner(2); };
    int &ref = a;
    const int &cref = b;
    int result = add(1, 2) + mixed(3);
    return result;
}
