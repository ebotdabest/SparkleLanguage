from lexer import lexer as l
from parser import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit

tokens = l.get_tokens("""
int main() -> useless {
    
}
""")
ast = p.build_ast(tokens)

if isinstance(ast, p.ParseError):
    print(ast)
else:
    module = compile_code(ast)
    # print(module)
    execute_with_jit(module)