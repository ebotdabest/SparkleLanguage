from lexer import lexer as l
import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit
from parser import VariableRefrence, VarDeclr

SCRIPT = """
int main() {
    print("be happy bitch");
    return 0;
}
"""

tokens = l.get_tokens(SCRIPT)

ast = p.build_ast(tokens)

if isinstance(ast, p.ParseError):
    print("Error raised!!!", ast.reason)
else:
    module = compile_code(ast)
    # print(module)
    engine = execute_with_jit(module)

    import ctypes as ct
    main_func_ptr = engine.get_function_address("main")

    main_func = ct.CFUNCTYPE(ct.c_int)(main_func_ptr)
    main_func()