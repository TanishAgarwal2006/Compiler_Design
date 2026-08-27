VENV_PYTHON = ./venv/bin/python
PYTHON ?= $(shell if [ -x "$(VENV_PYTHON)" ]; then echo "$(VENV_PYTHON)"; else echo "python3"; fi)
MAIN    = src/main.py
LEXER   = src/phase1_lexical_analysis/run_lexer.py
PARSER  = src/phase2_syntax_analysis/run_parser.py


# Usage: make lex FILE=tests/phase2_syntax/valid/02_if_else.c
lex:
	$(PYTHON) $(LEXER) $(FILE)

# Run lexical analysis ONLY for all Phase 1 test cases
lex-phase1:
	$(PYTHON) $(LEXER) --phase1

# Run lexical analysis ONLY across all test cases
lex-all:
	$(PYTHON) $(LEXER) --all

# Usage: make parse FILE=tests/phase2_syntax/valid/02_if_else.c
parse:
	$(PYTHON) $(PARSER) $(FILE)

# Run syntax analysis ONLY for Phase 2 test cases
parse-phase2:
	$(PYTHON) $(PARSER) --phase2

# Run syntax analysis ONLY across all test cases
parse-all:
	$(PYTHON) $(PARSER) --all

# Usage: make run FILE=tests/phase2_syntax/valid/11_recursive_function_call.c
run:
	$(PYTHON) $(MAIN) $(FILE) --all

# Run BOTH Lexical + Syntax Analysis across all test cases
run-all:
	./run.sh

# Runs the full automated test suite and reports PASS/FAIL per file
test:
	$(PYTHON) tests/run_tests.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "parsetab.py" -delete
	find . -name "parser.out" -delete
	rm -rf logs/ output.txt ast_log.txt *.log *_tokens.txt


.PHONY: lex lex-phase1 lex-all parse parse-phase2 parse-all run run-all test clean



