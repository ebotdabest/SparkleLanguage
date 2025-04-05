from lexer import lexer as l
from parser import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit

tokens = l.get_tokens("""
int test() {
    print("hello");
    return 2;
}


int main() -> useless {
    var hi = test();  
    var lol = 42;
    print("printing hi");
    print(hi);
    print("done");
    print(lol);
}
""")
# print(tokens)
ast = p.build_ast(tokens)
print(type(ast[1].elements[0].value))
if isinstance(ast, p.ParseError):
    print(ast)
else:
    module = compile_code(ast)
    print(module)
    execute_with_jit(module)