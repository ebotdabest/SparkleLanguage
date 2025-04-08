from lexer import lexer as l
import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit
from parser import VariableRefrence, VarDeclr

tokens = l.get_tokens("""
int sqr(int a) {
    return a * a;
}

int taket(int v) {
    return v-2;
}

int main() {
    const test_call = taket(sqr(2));
    
    return test_call;
}
""")
# print(tokens)
ast = p.build_ast(tokens)
print(ast[2].elements[0].value.args[0])
# print("apple")
# print(ast[1].elements[0])
if isinstance(ast, p.ParseError):
    print("Error raised!!!", ast.reason)
else:
    module = compile_code(ast)
    print(module)
    engine = execute_with_jit(module)
    import ctypes as ct
    main_func_ptr = engine.get_function_address("main")

    main_func = ct.CFUNCTYPE(ct.c_int)(main_func_ptr)
    print(main_func())