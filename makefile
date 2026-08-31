VENV_PYTHON = ./venv/bin/python
PYTHON ?= $(shell if [ -x "$(VENV_PYTHON)" ]; then echo "$(VENV_PYTHON)"; else echo "python3"; fi)
MAIN    = src/main.py
LEXER   = src/phase1_lexical_analysis/run_lexer.py
PARSER  = src/phase2_syntax_analysis/run_parser.py

lex:
	$(PYTHON) $(LEXER) $(FILE)

lex-phase1:
	$(PYTHON) $(LEXER) --phase1

lex-all:
	$(PYTHON) $(LEXER) --all

parse:
	$(PYTHON) $(PARSER) $(FILE)

parse-phase2:
	$(PYTHON) $(PARSER) --phase2

parse-all:
	$(PYTHON) $(PARSER) --all

run:
	$(PYTHON) $(MAIN) $(FILE) --all

run-all:
	./run.sh

test:
	$(PYTHON) tests/run_tests.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "parsetab.py" -delete
	find . -name "parser.out" -delete
	rm -rf logs/ output.txt ast_log.txt *.log *_tokens.txt
.PHONY: lex lex-phase1 lex-all parse parse-phase2 parse-all run run-all test clean


