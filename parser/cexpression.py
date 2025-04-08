from typing import List
from .ltypes import Constant, VariableRefrence
from utils import is_string
from lexer.token import PRECEDENCE, BASIC_KEYWORDS
from lexer.lexer import get_tokens
from .ltypes import BinaryOP, UnaryOP, FuncCall, EmptyOP

def get_segments(tokens: List[str]):
    """
    Creates segments that represent an instruction.
    :param tokens:
    :return:
    """
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

def parse_primary(tokens):
    """
    Parses a primary expression, including:
    - constants
    - strings
    - variables
    - unary minus
    - parentheses
    :param tokens: list of tokens
    :return: parsed expression node
    """
    tok = tokens.pop(0)


    # Handle parenthesized expressions
    if tok == '(':
        expr = parse_expression(tokens)
        if not tokens or tokens.pop(0) != ')':
            raise SyntaxError("Expected ')'")
        return expr

    if tok == '-':
        operand = parse_primary(tokens)
        return UnaryOP(operand, '-')
    elif tok == "+":
        operand = parse_primary(tokens)
        return UnaryOP(operand, '+')

    if tok.isdigit():
        return Constant(int(tok))

    if is_string(tok):
        return Constant(tok)

    if len(tokens) != 0 and tokens[-1] == BASIC_KEYWORDS[7]:
        func_name = tok

        args_formatted = []
        for argi in range(1, len(tokens) - 1, 2):
            args_formatted.append(parse_expression(get_tokens(tokens[argi])))

        return FuncCall(func_name, args_formatted)


    return VariableRefrence(tok)

def parse_expression(tokens, min_precedence=0):
    """
    Can parse expressions mainly mathematical
    :param tokens:
    :param min_precedence:
    :return:
    """

    lhs = parse_primary(tokens)

    while tokens and tokens[0] in PRECEDENCE and PRECEDENCE[tokens[0]] >= min_precedence:
        op = tokens.pop(0)
        precedence = PRECEDENCE[op]

        rhs = parse_expression(tokens, precedence + 1)

        lhs = BinaryOP(lhs, rhs, op)

    return lhs