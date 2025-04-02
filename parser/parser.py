from typing import List
from lexer.token import VARIABLE_MODIFIERS, VARIABLE_DECLARTOR, MUTABLE_DECLATOR, VARIABLE_SHIT

def get_segments(tokens: List[str]):
    segments = []
    segment = []
    for t in tokens:
        if t == ";":
            segments.append(segment)
            segment = []
        else:
            segment.append(t)

    return segments   

def build_ast(tokens: List[str]):
    segments = get_segments(tokens)

    for s in segments:
        if s[0] in VARIABLE_SHIT:
            i = 0
            modifiers = []
            while s[i] in VARIABLE_SHIT:
                modifiers.append(s[i])
                i += 1
            print(s, modifiers)


    return segments