BASIC_KEYWORDS = [
    "+",
    "-",
    "*",
    "/",
    ";",
    "=",
    "(",
    ")",
    ",",
    "->",
    "{",
    "}",
    "&&",
    "||",
    "[",
    "]"
]

OTHER_KEYWORDS = [
    "void",
    "class"
]

VARIABLE_DECLARTOR = ["var"]
MUTABLE_DECLATOR = ["const"]

BUILTIN_TYPES = [
    "stringstr",
    "stringchar",
    "int"
]

RETURN_MODIFIERS = [
    "useless"
]

BUILTIN_FUNCTIONS = [
    "print"
]

VARIABLE_SHIT = (*MUTABLE_DECLATOR, *VARIABLE_DECLARTOR)
KEYWORDS = (BASIC_KEYWORDS + VARIABLE_DECLARTOR + MUTABLE_DECLATOR + RETURN_MODIFIERS)