from typing import List
from .ltypes import Constant, VariableRefrence
from utils import is_string
from lexer.token import PRECEDENCE, BASIC_KEYWORDS
from lexer.lexer import get_tokens
from .ltypes import BinaryOP, UnaryOP, FuncCall, EmptyOP, StringOP
from copy import deepcopy

def get_segments(tokens: List[str]):
    """
    Creates segments that represent an instruction.
    :param tokens:
    :return:
    """
    segments = []
    segment = []
    depth = 0

    skip = False

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if skip:
            if t == '*/':
                skip = False
            i += 1
            continue
        elif t == '/*':
            skip = True
            i += 1
            continue
        elif t == '{':
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
        i += 1

    if segment:
        segments.append(segment)

    return segments


def parse_primary(tokens):
    tok = tokens.pop(0)

    if tok == '(':
        expr = parse_expression(tokens)
        if not tokens or tokens.pop(0) != ')':
            raise SyntaxError("Expected ')'")
        return expr

    if tok == '-':
        operand = parse_primary(tokens)
        return UnaryOP(operand, '-')
    elif tok == '+':
        operand = parse_primary(tokens)
        return UnaryOP(operand, '+')

    if tok.isdigit():
        node = Constant(int(tok))
    elif is_string(tok):
        node = Constant(tok)
    else:
        node = VariableRefrence(tok)

    while tokens and tokens[0] == '.':
        tokens.pop(0)
        if not tokens:
            raise SyntaxError("Expected attribute/method name after '.'")

        attr = tokens.pop(0)

        if tokens and tokens[0] == '(':
            tokens.pop(0)
            args = []
            current_arg = []
            paren_depth = 0
            while tokens:
                tok = tokens.pop(0)
                if tok == '(':
                    paren_depth += 1
                    current_arg.append(tok)
                elif tok == ')':
                    if paren_depth == 0:
                        if current_arg:
                            args.append(parse_expression(current_arg))
                        break
                    else:
                        paren_depth -= 1
                        current_arg.append(tok)
                elif tok == ',' and paren_depth == 0:
                    args.append(parse_expression(current_arg))
                    current_arg = []
                else:
                    current_arg.append(tok)
            node = FuncCall(attr, [node] + args)

    return node


def parse_expression(tokens, min_precedence=0):
    lhs = parse_primary(tokens)

    while tokens and tokens[0] in PRECEDENCE and PRECEDENCE[tokens[0]] >= min_precedence:
        op = tokens.pop(0)
        precedence = PRECEDENCE[op]
        rhs = parse_expression(tokens, precedence + 1)

        if isinstance(lhs, Constant) and lhs.type == "str":
            lhs = StringOP(lhs, rhs, op)
        elif isinstance(rhs, Constant) and rhs.type == "str":
            lhs = StringOP(lhs, rhs, op)
        else:
            lhs = BinaryOP(lhs, rhs, op)

    return lhs