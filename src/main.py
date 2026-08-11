import sys

from lexer import lexer
from utils.token import reserved
from utils.errors import lex_errors, clear_errors

# Store keyword token types once
KEYWORD_TOKENS = set(reserved.values())


def main():
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)

    filename = sys.argv[1]

    # opening file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)

    # Resetting lexer state for next input file
    lexer.lineno = 1
    clear_errors()
    lexer.input(code)
    tokens_list = []

    # Tokenization
    while True:
        tok = lexer.token()

        if not tok:
            break
        if tok.type in KEYWORD_TOKENS:
            display_type = "keyword"
        elif tok.type == "IDENTIFIER":
            display_type = "identifier"
        else:
            display_type = tok.type.lower()

        tokens_list.append((tok.value, display_type))

    # Output
    if lex_errors:

        print("--- Lexical Errors Detected ---")
        for err in lex_errors:
            print(err)
    else:
        print(f"{'Lexeme':<25} {'Token':<20}")
        print("-" * 45)

        for lexeme, token in tokens_list:
            print(f"{str(lexeme):<25} {token:<20}")


if __name__ == "__main__":
    main()