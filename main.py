from lexer import lexer as l
import parser as p
from pprint import pprint
from compiler import compile_code, execute_with_jit
from parser import VariableRefrence, VarDeclr

SCRIPT = """
str stuff(str cuccos) {
    return cuccos + "hali";
}

int main() {
    const asd = 24;
    asd = 12;
    var shit = stuff("hali");
    print("%s\n", shit);
    print("%s\n",stuff("hali"));
    return asd;
}
"""

tokens = l.get_tokens(SCRIPT)
# print(tokens)
ast = p.build_ast(tokens)
print(type(ast[0].elements[0].value))
# print(type(ast[2].elements[0].value.args[0].args[0]))
# print("apple")
# print(ast[1].elements[0])
if isinstance(ast, p.ParseError):
    print("Error raised!!!", ast.reason)
else:
    module = compile_code(ast)
    print(module)
    # engine = execute_with_jit(module)
    # import ctypes as ct
    # main_func_ptr = engine.get_function_address("main")
    #
    # main_func = ct.CFUNCTYPE(ct.c_int)(main_func_ptr)
    # print(main_func())