PYTHON = ./venv/bin/python
MAIN = src/main.py
TEST_DIR = test


run:
	$(PYTHON) $(MAIN) $(FILE)


test:
	@echo "Running all lexer test cases..."
	@echo ""

	@for file in $(TEST_DIR)/*.c; do \
		echo "========================================"; \
		echo "Testing $$file"; \
		echo "========================================"; \
		$(PYTHON) $(MAIN) $$file; \
		echo ""; \
	done


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete


.PHONY: run test clean