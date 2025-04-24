from lexer.token import VARIABLE_SHIT, BUILTIN_TYPES, OTHER_KEYWORDS, BASIC_KEYWORDS
from .ltypes import *
from .error import ParseError
from lexer.lexer import get_tokens
from .cexpression import *
from typing import List, Dict


def parse_segment(segment, allow_return = False, lscope: Scope = None, gscope: Scope = None, runner=None):
    if segment[0] in VARIABLE_SHIT:
        # Defining a variable, handles scope as a hint
        var_type = segment[0]
        var_name = segment[1]
        if lscope:
            for v in lscope.variables:
                if v.name == var_name:
                    runner.stop(ParseError("Variable double reassignment xd"))

        for v in gscope.variables:
            if v.name == var_name:
                runner.stop(ParseError("Variable double reassignment xd"))

        if segment[-1] == ";": segment.pop(-1)
        expression = segment[3:len(segment)]

        if len(expression) == 1:
            expr = expression[0]

            def get_declaration():
                if expr.isdigit():
                    return VarDeclr(var_name, Constant(int(expr)), var_type == "var")
                if is_string(expr):
                    return VarDeclr(var_name, Constant(expr), var_type == "var")

                if expr.endswith("()") and expr[:-2].isidentifier():
                    fname = expr[:-2]
                    return VarDeclr(var_name, FuncCall(fname, []), var_type == "var")

                if expr.isidentifier():
                    return VarDeclr(var_name, VariableRefrence(expr), var_type == "var")

                return VarDeclr(var_name, Constant(expr), var_type == "var")

            declr = get_declaration()
            if lscope:
                lscope.declare_variable(declr)
            else:
                gscope.declare_variable(declr)
            return declr

        value = parse_expression(expression)
        declr = VarDeclr(var_name, value, var_type == "var")
        if lscope:
            lscope.declare_variable(declr)
        else:
            gscope.declare_variable(declr)
        return declr
    elif segment[0] in BUILTIN_TYPES or segment == OTHER_KEYWORDS[0]:
        # Creating a function
        func_type = segment[0]
        func_name = segment[1]
        args = []
        if segment[2] != BASIC_KEYWORDS[6]:
            runner.stop(ParseError("Must be an opening"))
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
        sc = Scope()
        elements = [parse_segment(inst, True, sc, gscope, runner) for inst in instructions]
        return FuncDeclr(func_name, func_type, args, elements, return_modifier_type, sc)
    elif segment[0] == OTHER_KEYWORDS[2] and allow_return:
        expr_token = segment[1:len(segment)]
        expr = parse_expression(expr_token)

        # if expr_token.isnumeric():
        #     return ReturnValue(Constant(int(expr_token)))
        #
        # if is_string(expr_token):
        #     return ReturnValue(Constant(expr_token))
        #
        # if expr_token.isidentifier():
        #     return ReturnValue(VariableRefrence(expr_token))


        return ReturnValue(expr)
    elif segment[1] == "=":
        var_name = segment[0]
        if lscope:
            # We are currently inside a function
            for v in lscope.variables:
                if v.name == var_name and not v.is_mutable:
                    runner.stop(ParseError("Immutability detected opinion rejected"))

        for v in gscope.variables:
            if v.name == var_name and not v.is_mutable:
                runner.stop(ParseError("Immutability detected opinion rejected"))

        expression = []

        for s in segment[2:len(segment)]: expression.append(s)

        value = parse_expression(expression)

        return ReassignVariable(var_name, value)
    else:
        func_name = segment[0]
        start, end = 1, -2

        arg_tokens = []
        nested_level = 0
        current_arg = []
        for token in segment[start + 1:-1]:
            if token == '(':
                nested_level += 1
            elif token == ')':
                nested_level -= 1
            if token == ',' and nested_level == 0:
                arg_tokens.append(current_arg)
                current_arg = []
            else:
                current_arg.append(token)
        if current_arg:
            arg_tokens.append(current_arg)

        args = [parse_expression(arg) for arg in arg_tokens]
        # for i in range(1, len(segment)):
        #     if segment[i] == BASIC_KEYWORDS[7]:
        #         end = i
        #
        # args_raw,arg = [], []
        # for i in range(start + 1, end):
        #     if segment[i] == BASIC_KEYWORDS[8]:
        #         args_raw.append("".join(arg))
        #         arg = []
        #     else:
        #         arg.append(segment[i])
        # else:
        #     args_raw.append("".join(arg))
        #
        # args = []
        # if end - (start + 1) > 0:
        #     args_raw, arg = [], []
        #     for i in range(start + 1, end):
        #         if segment[i] == BASIC_KEYWORDS[8]:  # if ","
        #             args_raw.append("".join(arg))
        #             arg = []
        #         else:
        #             arg.append(segment[i])
        #     else:
        #         if arg:
        #             args_raw.append("".join(arg))
        #
        #     for a in args_raw:
        #         if a.isnumeric():
        #             args.append(Constant(int(a)))
        #         elif is_string(a):
        #             args.append(Constant(a))
        #         elif a.strip():
        #             args.append(parse_expression(get_tokens(a)))
        #
        return FuncCall(func_name, args)

class SegmentRunnerUntilError:
    def __init__(self, segments):
        self.seg = segments
        self.i = 0
        self.stopped = False
        self.error = None
        self.error_yielded = False

    def reset(self):
        self.i = 0
        self.stopped = False
        self.error = None
        self.error_yielded = False

    def __iter__(self):
        while self.i < len(self.seg):
            if self.stopped:
                if not self.error_yielded:
                    self.error_yielded = True
                    yield self.error
                break
            yield self.seg[self.i]
            self.i += 1

    def stop(self, err):
        self.stopped = True
        self.error = err

def build_ast(tokens: List[str]):
    gscope = Scope()
    segments = get_segments(tokens)
    ast = []
    runner = SegmentRunnerUntilError(segments)
    for s in runner:
        if isinstance(s, ParseError):
            return s
        parsed = parse_segment(s, gscope=gscope, runner=runner)
        ast.append(parsed)

    return ast