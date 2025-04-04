from lexer import lexer as l
from parser import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit

tokens = l.get_tokens("""
int main() {
    var x = 79;
    print(x);
    print("Ducking is unsafe");
    
    return x;    
}
""")
ast = p.build_ast(tokens)

if isinstance(ast, p.ParseError):
    print(ast)
else:
    module = compile_code(ast)
    # print(module)
    execute_with_jit(module)