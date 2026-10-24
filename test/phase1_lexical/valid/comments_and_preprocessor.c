/* Lexical analysis: comments and preprocessor lines are skipped. */
#include <stdio.h>
#include "local.h"
#define MAX 10
#define SQUARE(x) ((x) * (x))
#undef MAX
#ifdef FLAG
#ifndef OTHER
#if 1
#elif 0
#else
#endif
#endif
#endif
#pragma once
#  include <stdlib.h>
#line 5
#warning just a note
#error never reached by the lexer
// line comment at top level
int a; // trailing line comment
int /* inline block comment */ b;
/* block comment
   spanning
   several lines */
int c;
/* comment with // inside */ int d;
// comment with /* inside
int e;
/**/ int f;
/*** many stars ***/ int g;
int main() { return 0; } // last line comment
