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
    "]",
    "+=",
    "-=",
    "*=",
    "/=",
    "//",
    "/*",
    "*/",
    "."

]

OTHER_KEYWORDS = [
    "void",
    "class",
    "return"
]

VARIABLE_DECLARTOR = ["var"]
MUTABLE_DECLATOR = ["const"]

BUILTIN_TYPES = [
    "str",
    "char",
    "int"
]

RETURN_MODIFIERS = [
    "useless",
    "extern"
]


VARIABLE_SHIT = (*MUTABLE_DECLATOR, *VARIABLE_DECLARTOR)
KEYWORDS = (BASIC_KEYWORDS + VARIABLE_DECLARTOR + MUTABLE_DECLATOR + RETURN_MODIFIERS + OTHER_KEYWORDS)

PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
}