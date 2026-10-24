#!/bin/bash
# One log file per test case, holding everything the compiler can say about it:
# lex table + symbols + AST (--all), symbol table with offsets (--semantic), IR (--tac), program output (run).
#   tools/mklog.sh 1|2|3|all     every case of that phase   -> out/logs/phaseN/<valid|invalid>/<case>.log
#   tools/mklog.sh FILE.c        one case                   -> out/logs/<case>.log
cd "$(dirname "$0")/.."
[ -x bin/tacgen ] || make >/dev/null
RUN="python3 src/phase3_intermediate_code/tac_interpreter.py"
caselog() {  # source file, log file
  f=$1; b=${f%.c}; mkdir -p "$(dirname "$2")"
  { for o in --all --semantic --tac; do echo "######## $o"; bin/tacgen "$f" $o 2>&1; done
    echo "######## run"
    if bin/tacgen "$f" -o out/x.ir >/dev/null 2>&1; then
      $RUN out/x.ir $(cat $b.args 2>/dev/null) < $([ -f $b.in ] && echo $b.in || echo /dev/null) 2>&1
    else echo "(not compiled: see the errors above)"; fi
  } > "$2"; echo "$2"
}
mkdir -p out
case $1 in
  *.c) caselog "$1" "out/logs/$(basename "${1%.c}").log" ;;
  *) for p in $([ "$1" = all ] && echo 1 2 3 || echo "$1"); do
       d=$(ls -d test/phase${p}_*)
       for f in $d/*/*.c $d/*/*/*.c; do
         [ -f "$f" ] || continue
         r=${f#$d/}; caselog "$f" "out/logs/phase$p/${r%.c}.log"
       done
     done ;;
esac
exit 0
