// Lexical errors in numbers. Every numbered line below is one deliberate bug.
int ok1 = 1;
int a = 089;            // 1: octal literal with digit 8
int b = 0b1102;         // 2: binary literal with digit 2
int c = 0x;             // 3: hex literal without digits
int d = 0b;             // 4: binary literal without digits
float e = 1.2.3;        // 5: two decimal points
float f = 1e;           // 6: exponent without digits
int g = 12abc;          // 7: letters glued to a number
int h = 0xFG;           // 8: bad hex digit
int i = 45UU;           // 9: bad suffix
int ok2 = 2;
