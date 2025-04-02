from lexer import lexer as l
from parser import parser as p
from pprint import pprint

tokens = l.get_tokens("""
var public nonlocal x = 5+6;
public var nonlocal b = 4*2/8;
const sanyi = 69;
print(x+b);
print("fuck you", "twice");
""")

pprint(p.build_ast(tokens), indent=2)