from typing import Tuple, Optional

class Constant:
    def __init__(self, value):
        self.value = value

class VariableRefrence:
    def __init__(self, ref):
        self.value = ref

class BinaryOP:
    def __init__(self, left: Constant | VariableRefrence | Optional["BinaryOP"], right: Constant | VariableRefrence | Optional["BinaryOP"], operator):
        self.left = left
        self.right = right
        self.operator = operator

class VarDeclr:
    def __init__(self, name, value: Constant | VariableRefrence | BinaryOP, is_mutable: bool):
        self.name: str = name
        self.value: Constant | VariableRefrence | BinaryOP = value
        self.is_mutable: bool = is_mutable