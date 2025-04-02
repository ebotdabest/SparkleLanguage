BASIC_KEYWORDS = [
    "+",
    "-",
    "*",
    "/",
    ";",
    "=",
    "(",
    ")",
    ","
]

VARIABLE_DECLARTOR = ["var"]
MUTABLE_DECLATOR = ["const"]
VARIABLE_MODIFIERS = [
    "nonlocal",
    "private",
    "public",
    "local"
]

VARIABLE_SHIT = (*VARIABLE_MODIFIERS, *MUTABLE_DECLATOR, *VARIABLE_DECLARTOR)
KEYWORDS = BASIC_KEYWORDS + VARIABLE_DECLARTOR + VARIABLE_MODIFIERS + MUTABLE_DECLATOR