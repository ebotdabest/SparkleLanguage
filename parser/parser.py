from ast import Param
from typing import List, Dict, Any, final
from lexer.token import VARIABLE_DECLARTOR, MUTABLE_DECLATOR, VARIABLE_SHIT, BUILTIN_TYPES, OTHER_KEYWORDS, PRECEDENCE, BASIC_KEYWORDS
from .ltypes import Constant, BinaryOP, VariableRefrence, VarDeclr, FuncDeclr, FuncArg, FuncCall, ReturnValue
from .error import ParseError
from utils import is_string
from lexer.lexer import get_tokens

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

def parse_primary(tokens):
    tok = tokens.pop(0)
    if tok.isdigit():
        return Constant(int(tok))
    if is_string(tok):
        return Constant(tok)
    return VariableRefrence(tok)

def parse_expression(tokens, min_precedence=0):
    lhs = parse_primary(tokens)

    while tokens and tokens[0] in PRECEDENCE and PRECEDENCE[tokens[0]] >= min_precedence:
        op = tokens.pop(0)
        precedence = PRECEDENCE[op]

        rhs = parse_expression(tokens, precedence + 1)

        lhs = BinaryOP(lhs, rhs, op)

    return lhs


def parse_segment(segment, allow_return = False):
    if segment[0] in VARIABLE_SHIT:
        var_type = segment[0]
        var_name = segment[1]
        if segment[-1] == ";": segment.pop(-1)
        expression = segment[3:len(segment)]

        if len(expression) == 1:
            expr = expression[0]
            if expr.isdigit():
                return VarDeclr(var_name, Constant(int(expr)), var_type == "var")
            if is_string(expr):
                return VarDeclr(var_name, Constant(expr), var_type == "var")
            if expr.isidentifier():
                return VarDeclr(var_name, VariableRefrence(expr), var_type == "var")

            return VarDeclr(var_name, Constant(expr), var_type == "var")
        value = parse_expression(expression)
        return VarDeclr(var_name, value, var_type == "var")

    elif segment[0] in BUILTIN_TYPES or segment == OTHER_KEYWORDS[0]:
        func_type = segment[0]
        func_name = segment[1]
        args = []
        if segment[2] != BASIC_KEYWORDS[6]:
            return False
        if segment[3] != BASIC_KEYWORDS[7]:
            end_of_args = 0
            for i in range(3, len(segment)):
                if segment[i] == BASIC_KEYWORDS[7]:
                    end_of_args = i
                    break

            arg_list = segment[3:end_of_args]
            arg_making, arg_formatted = [], []

            for arg in range(0, len(arg_list)):
                if arg_list[arg] == ",":
                    arg_formatted.append(arg_making)
                    arg_making = []
                else:
                    arg_making.append(arg_list[arg])
            else:
                arg_formatted.append(arg_making)

            args = [FuncArg(n, t) for t, n in arg_formatted]

        return_modifier = -1

        for i in range(0, len(segment)):
            if segment[i] == BASIC_KEYWORDS[9]:
                return_modifier = i
                break

        return_modifier_type = ""
        if return_modifier != -1: return_modifier_type = segment[return_modifier + 1]

        start, end = 0, len(segment) - 1

        for i in range(0, len(segment)):
            if segment[i] == BASIC_KEYWORDS[10]:
                start = i + 1

        instructions = []
        instruction = []
        for inst in range(start, end):
            if segment[inst] == ";":
                instructions.append(instruction)
                instruction = []
            else:
                instruction.append(segment[inst])

        return FuncDeclr(func_name, func_type, args, [parse_segment(inst, True) for inst in instructions], return_modifier_type)
    elif segment[0] == OTHER_KEYWORDS[2] and allow_return:
        expr_token = segment[1]

        if expr_token.isnumeric():
            return ReturnValue(Constant(int(expr_token)))

        if is_string(expr_token):
            return ReturnValue(Constant(expr_token))

        if expr_token.isidentifier():
            return ReturnValue(VariableRefrence(expr_token))


        return ReturnValue(Constant(28))

    else:
        func_name = segment[0]
        start, end = 1, 0
        for i in range(1, len(segment)):
            if segment[i] == BASIC_KEYWORDS[7]:
                end = i

        args_raw,arg = [], []
        for i in range(start + 1, end):
            if segment[i] == BASIC_KEYWORDS[8]:
                args_raw.append("".join(arg))
                arg = []
            else:
                arg.append(segment[i])
        else:
            args_raw.append("".join(arg))

        args = []
        for a in args_raw:
            if a.isnumeric():
                args.append(Constant(int(a)))
                continue
            if is_string(a):
                args.append(Constant(a))
                continue

            args.append(parse_expression(get_tokens(a)))

        return FuncCall(func_name, args)

def build_ast(tokens: List[str]):
    segments = get_segments(tokens)
    ast = []
    for s in segments:
        parsed = parse_segment(s)
        if not parsed:
            return ParseError("Invalid usage idk")
        ast.append(parsed)

    return ast