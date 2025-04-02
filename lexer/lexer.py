from typing import List
from lexer.token import KEYWORDS

def get_tokens(source: str) -> List[str]:
    tokens = []
    lexeme = ''
    i = 0
    while i < len(source):
        c = source[i]

        if c.isspace():
            if lexeme:
                tokens.append(lexeme)
                lexeme = ''
            i += 1
            continue

        if c == '"':
            end = i + 1
            while end < len(source) and source[end] != '"':
                end += 1
            tokens.append(source[i:end+1])
            i = end + 1
            continue

        matched = False
        for kw in sorted(KEYWORDS, key=len, reverse=True):
            if source.startswith(kw, i):
                if lexeme:
                    tokens.append(lexeme)
                    lexeme = ''
                tokens.append(kw)
                i += len(kw)
                matched = True
                break
        if matched:
            continue

        lexeme += c
        i += 1

    if lexeme:
        tokens.append(lexeme)

    return tokens
