from typing import Tuple, Optional, List


def auto_str(format="<name>: <value>", sep="; "):
    def iter_over(instance):
        formatted = [format.replace("<name>", str(k)).replace("<value>", str(v)) for k, v in vars(instance).items()]

        return sep.join(formatted)

    def wrapper(cls):
        cls.__str__ = iter_over
        return cls

    return wrapper

class Constant:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        if type(self._value) == str:
            v: str = self._value
            return v.replace('"', "", 1).replace("'", "", 1)[::-1] \
                .replace('"', "", 1).replace("'", "", 1)[::-1]
        return self._value

    @property
    def type(self) -> str:
        return type(self.value).__name__

    def __str__(self):
        return f"c: {self.value}"

@auto_str()
class VariableRefrence:
    def __init__(self, ref):
        self.value = ref

class BinaryOP:
    def __init__(self, left: Constant | VariableRefrence | Optional["BinaryOP"], right: Constant | VariableRefrence | Optional["BinaryOP"], operator):
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self):
        return f"left: [{str(self.left)}]; right: [{str(self.right)}]; operator: {self.operator}"

@auto_str()
class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class VarDeclr:
    def __init__(self, name, value: Constant | VariableRefrence | BinaryOP | FuncCall, is_mutable: bool):
        self.name: str = name
        self.value: Constant | VariableRefrence | BinaryOP = value
        self.is_mutable: bool = is_mutable

    def __str__(self):
        return f"Var: {self.name};{str(self.value)};{self.is_mutable}"

@auto_str()
class Scope:
    def __init__(self):
        self.variables: List[VarDeclr] = []
        self.functions: List[FuncDeclr] = []

    def declare_variable(self, var):
        self.variables.append(var)

    def declare_func(self, func):
        self.functions.append(func)


@auto_str()
class FuncDeclr:
    def __init__(self, name, return_type, args, elements, return_modifier, scope):
        self.name = name
        self.return_type = return_type
        self.elements = elements
        self.args: List[FuncArg] = args
        self.return_modifier = return_modifier
        self.scope = scope

@auto_str()
class FuncArg:
    def __init__(self, name, tpe):
        self.name = name
        self.tpe = tpe

@auto_str()
class ReturnValue:
    def __init__(self, v):
        self.value = v

@auto_str()
class ReassignVariable:
    def __init__(self, var_name, value):
        self.var = var_name
        self.value = value

@auto_str()
class UnaryOP:
    def __init__(self, operand, operator):
        self.operand = operand
        self.operator = operator

class EmptyOP:
    ...

@auto_str()
class StringOP:
    def __init__(self, lhs, rhs, op):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

