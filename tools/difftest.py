"""difftest.py PROJ file.c ...  : compile with gcc and with our compiler; compare stdout+exit code."""
import subprocess, sys, os, tempfile
proj=sys.argv[1]; files=sys.argv[2:]
env=dict(os.environ)
bad=0
for f in files:
    base=f[:-2]
    inp=open(base+".in").read() if os.path.exists(base+".in") else ""
    args=open(base+".args").read().split() if os.path.exists(base+".args") else []
    tmp=tempfile.mkdtemp()
    g=subprocess.run(["gcc","-w","-fwrapv","-std=gnu11","-include","stdbool.h","-o",tmp+"/a.out",f,"-lm"],capture_output=True,text=True)
    if g.returncode: print("GCC-FAIL",f,g.stderr[:300]); bad+=1; continue
    ge=subprocess.run([tmp+"/a.out"]+args,input=inp,capture_output=True,text=True,timeout=5)
    c=subprocess.run(["python3",proj+"/src/main.py",f,"-o",tmp+"/p.ir"],capture_output=True,text=True,env=env)
    if c.returncode:
        print("COMPILE-FAIL",f,"\n   ",c.stderr.strip().replace("\n","\n    ")[:600]); bad+=1; continue
    r=subprocess.run(["python3",proj+"/src/phase3_intermediate_code/tac_interpreter.py",tmp+"/p.ir"]+args,input=inp,capture_output=True,text=True,env=env,timeout=120)
    if r.stdout!=ge.stdout or (r.returncode&0xFF)!=(ge.returncode&0xFF):
        print("MISMATCH",f,"rc gcc=%d ours=%d"%(ge.returncode,r.returncode))
        import difflib
        for l in list(difflib.unified_diff(ge.stdout.splitlines(),r.stdout.splitlines(),"gcc","ours",lineterm="",n=0))[:12]: print("   ",l)
        if r.stderr: print("    stderr:",r.stderr[:300])
        bad+=1
    else: print("ok",f)
print("BAD:",bad)
