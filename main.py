from lexer import lexer as l
from parser import parser as p

tokens = l.get_tokens("""
var public nonlocal x = 5+6;
var nonlocal b = 4*2/8;
print(x+b);
print("fuck you", "twice");
""")

print(p.build_ast(tokens))