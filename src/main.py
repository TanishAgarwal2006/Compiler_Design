import sys
from lexer import lexer, lex_errors, reserved


def main():

    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)

    filename = sys.argv[1]

    # Opening the file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)


    # Reset lexer state for new input
    lexer.lineno = 1
    lex_errors.clear()
    lexer.input(code)
    tokens_list = []

    # Store keyword token types
    keyword_tokens = set(reserved.values())

    # Tokenization
    while True:
        tok = lexer.token()
        if not tok:
            break
        if tok.type in keyword_tokens:
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