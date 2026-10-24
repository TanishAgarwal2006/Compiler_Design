import random,sys
seed=int(sys.argv[1]); random.seed(seed)
V=["a","b","c","d"]; F=["f","g"]; A="arr"
def ie(d=0):
    r=random.random()
    if d>3 or r<0.25: return random.choice([str(random.randint(-20,200)),random.choice(V),"'a'"])
    if r<0.35: return f"{A}[({ie(d+1)})&3]"
    if r<0.45: return f"({random.choice(['-','~','!'])} {ie(d+1)})"
    if r<0.52: return f"(int)({fe(d+1)})"
    if r<0.6: return f"({ie(d+1)} ? {ie(d+1)} : {ie(d+1)})"
    op=random.choice(["+","-","*","&","|","^","<","<=","==","!=","&&","||",">",">="])
    if random.random()<0.1: op=random.choice(["/","%"]); return f"({ie(d+1)} {op} (({ie(d+1)}&7)+1))"
    if random.random()<0.1: return f"({ie(d+1)} {random.choice(['<<','>>'])} ({ie(d+1)}&15))"
    return f"({ie(d+1)} {op} {ie(d+1)})"
def fe(d=0):
    r=random.random()
    if d>3 or r<0.3: return random.choice(["1.5","0.25","2",random.choice(F),f"({ie(d+1)})"])
    return f"({fe(d+1)} {random.choice(['+','-','*'])} {fe(d+1)})"
def st(d=0):
    r=random.random()
    if d>2 or r<0.35:
        k=random.random()
        if k<.5: return f"{random.choice(V)} {random.choice(['=','+=','-=','^=','|=','&='])} {ie()};"
        if k<.7: return f"{A}[({ie()})&3] {random.choice(['=','+='])} {ie()};"
        if k<.85: return f"{random.choice(F)} = {fe()};"
        return f"{random.choice(V)}{random.choice(['++','--'])};"
    if r<.5: return f"if ({ie()}) {{ {st(d+1)} }} else {{ {st(d+1)} }}"
    if r<.65: return f"for (i{d}=0;i{d}<{random.randint(1,4)};i{d}++) {{ {st(d+1)} {st(d+1)} }}"
    if r<.75: return f"switch (({ie()})&3) {{ case 0: {st(d+1)} case 1: {st(d+1)} break; default: {st(d+1)} }}"
    return f'printf("%d %d\\n", {ie()}, {ie()});'
body="\n    ".join(st() for _ in range(12))
print(f'''#include <stdio.h>
int main(){{ int a=3,b=7,c=-5,d=100,i0,i1,i2; int arr[4]={{1,2,3,4}}; float f=1.5,g=0.25;
    {body}
    printf("%d %d %d %d %d %d %d %d\\n",a,b,c,d,arr[0],arr[1],arr[2],arr[3]); return 0; }}''')
