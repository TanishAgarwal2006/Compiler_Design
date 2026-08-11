# errors.py for storing lexical, syntax, and semantic errors encountered later

# Stores all lexical errors encountered during lexing
lex_errors = []
#temp lex_errors for now, can later replace with a generalized errors list with objects Error(phase, msg, line)

def add_lex_error(message):
    lex_errors.append(message)

def clear_errors():
    lex_errors.clear()