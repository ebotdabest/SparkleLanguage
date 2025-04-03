from lexer import lexer as l
from parser import parser as p
from pprint import pprint

tokens = l.get_tokens("""
var x = 5+6;
var b = 4*2/8;
const sanyi = 69;

int main() -> useless {
    print("hello");
    print("cica");
    print(12);
}
""")
print(tokens)
pprint(p.build_ast(tokens), indent=2)