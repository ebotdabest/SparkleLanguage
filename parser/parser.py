from typing import List, Dict
from lexer.token import VARIABLE_MODIFIERS, VARIABLE_DECLARTOR, MUTABLE_DECLATOR, VARIABLE_SHIT


def get_segments(tokens: List[str]):
    segments = []
    segment = []
    for t in tokens:
        if t == ";":
            segments.append(segment)
            segment = []
        else:
            segment.append(t)

    return segments   

def value_breakdown(value: str) -> Dict:
    breakdown = {
        "type": "unknown",
        "values:": []
    }
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        breakdown["type"] = "str_declr"


def build_ast(tokens: List[str]):
    segments = get_segments(tokens)
    ast = []    
    for s in segments:
        if s[0] in VARIABLE_SHIT:
            i = 0
            modifiers = []
            while s[i] in VARIABLE_SHIT:
                modifiers.append(s[i])
                i += 1
            name = s[len(modifiers)]
            value = "".join([s[sp] for sp in range(len(modifiers) +2, len(s))])

            ast.append({
                "type": "var_declr",
                "properties": {
                    "modifiers": modifiers,
                    "type": "var" if "var" in modifiers else "const",
                    "value": {
                        "raw": value
                    },
                    "name": name
                }
            })

    return ast