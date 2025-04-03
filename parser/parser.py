from typing import List, Dict, Any
from lexer.token import VARIABLE_DECLARTOR, MUTABLE_DECLATOR, VARIABLE_SHIT, BUILTIN_TYPES, OTHER_KEYWORDS
from .types import Constant, BinaryOP, VariableRefrence, VarDeclr

def get_segments(tokens: List[str]):
    segments = []
    segment = []
    depth = 0

    for t in tokens:
        if t == '{':
            depth += 1
            segment.append(t)
        elif t == '}':
            depth -= 1
            segment.append(t)
            if depth == 0 and segment:
                segments.append(segment)
                segment = []
        elif t == ';':
            segment.append(t)
            if depth == 0:
                segments.append(segment)
                segment = []
        else:
            segment.append(t)

    if segment:
        segments.append(segment)

    return segments

def parse_segment(segment):
    ast_part = None
    if segment[0] in VARIABLE_SHIT:
        var_type = segment[0]
        var_name = segment[1]
        expression = segment[3:len(segment)-1]
        if len(expression) == 1:
            return VarDeclr(var_name, Constant(expression[0]), var_type == "var")
        print(expression)
        # BinaryOP(Constant(expression[0]), Constant(expression[2]), expression[1])
        # BinaryOP(Constant(expression[0]), BinaryOP(Constant(expression[2]), Constant(expression[4]), expression[3]),
        #          expression[1])

        # for e in range(0, len(expression), 2):
        #     print(expression[e])
        #     if e > 0:
        #         print("operator: ", expression[e - 1])

    elif segment[0] in BUILTIN_TYPES or segment == OTHER_KEYWORDS[0]:
        print("function creation")

    return ast_part

def build_ast(tokens: List[str]):
    segments = get_segments(tokens)
    ast = []
    for s in segments:
        parse_segment(s)
        print("-"*20)

    return ast