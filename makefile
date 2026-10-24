PYTHON ?= $(shell [ -x venv/bin/python ] && echo venv/bin/python || echo python3)

all: bin/tacgen          # build the compiler launcher

bin/tacgen: src/main.py
	mkdir -p bin
	printf '#!/bin/sh\nPY=$$(dirname "$$0")/../venv/bin/python\n[ -x "$$PY" ] || PY=python3\nexec "$$PY" "$$(dirname "$$0")/../src/main.py" "$$@"\n' > $@
	chmod +x $@

setup:                   # one-time: virtual environment + PLY
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

test: all                # run every test case
	./run.sh bin/tacgen

show:                    # make show FILE=prog.c  -> tokens, tree, symbols
	$(PYTHON) src/main.py $(FILE) --all

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf bin out src/phase2_syntax_analysis/parsetab.py src/phase2_syntax_analysis/parser.out

log1 log2 log3 logall: bin/tacgen   # one log file per test case of that phase -> out/logs/ (see tools/mklog.sh)
	tools/mklog.sh $(patsubst logall,all,$(subst log,,$@))

logcase: bin/tacgen                 # make logcase FILE=test/phase3_tac/valid/functions/functions.c
	tools/mklog.sh $(FILE)
