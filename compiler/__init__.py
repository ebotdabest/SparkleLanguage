from llvmlite import ir, binding
from parser.ltypes import *
from typing import Dict

types = {
    "int": lambda bits=32: ir.IntType(bits),
    "str": lambda: ir.PointerType(ir.IntType(8))
}

def get_int_format_str(module, builder):
    fmt_str = "%d\n\0"
    byte_vals = [ir.IntType(8)(b) for b in fmt_str.encode("utf-8")]
    fmt_type = ir.ArrayType(ir.IntType(8), len(byte_vals))
    global_fmt = ir.GlobalVariable(module, fmt_type, name=".int_fmt")
    global_fmt.linkage = "internal"
    global_fmt.global_constant = True
    global_fmt.initializer = ir.Constant(fmt_type, byte_vals)
    global_fmt.unnamed_addr = True

    zero = ir.Constant(ir.IntType(32), 0)
    return builder.gep(global_fmt, [zero, zero], inbounds=True)

def get_ir_type(type_name: str):
    if type_name not in types:
        raise ValueError(f"Unsupported type: {type_name}")
    return types[type_name]()

def create_global_string(module, builder, string_value: str, name_hint: str):
    str_bytes = bytearray(string_value.encode('utf8')) + b'\00'
    const_array = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_bytes)),
                              [ir.IntType(8)(b) for b in str_bytes])

    global_str = ir.GlobalVariable(module, const_array.type, name=name_hint)
    global_str.linkage = 'internal'
    global_str.global_constant = True
    global_str.initializer = const_array
    global_str.unnamed_addr = True

    zero = ir.Constant(ir.IntType(32), 0)
    return builder.gep(global_str, [zero, zero], inbounds=True)

def compile_code(ast):
    module = ir.Module(name="program")
    variables: Dict[str, ir.Value] = {}

    puts_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
    puts_func = ir.Function(module, puts_ty, name="printf")

    fflush_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))])
    fflush_func = ir.Function(module, fflush_ty, name="fflush")

    for node in ast:
        if isinstance(node, FuncDeclr):
            compile_function(node, module, puts_func, fflush_func, variables, node.return_modifier)

    return module

def compile_function(func_decl, module, puts_func, fflush_func, outer_vars, return_modifier):
    arg_types = [get_ir_type(arg.tpe) for arg in func_decl.args]
    ret_type = get_ir_type(func_decl.return_type)
    func_type = ir.FunctionType(ret_type, arg_types)

    func = ir.Function(module, func_type, name=func_decl.name)
    block = func.append_basic_block("entry")
    builder = ir.IRBuilder(block)

    local_vars = dict(outer_vars)

    for arg, arg_decl in zip(func.args, func_decl.args):
        ptr = builder.alloca(arg.type, name=arg_decl.name)
        builder.store(arg, ptr)
        local_vars[arg_decl.name] = ptr

    for stmt in func_decl.elements:
        compile_statement(stmt, builder, module, local_vars, puts_func, fflush_func, return_modifier)

    if return_modifier == "useless":
        builder.ret(ir.Constant(ir.IntType(32), 0))

def compile_statement(stmt, builder, module, variables, puts_func, fflush_func, return_modifier):
    if isinstance(stmt, VarDeclr):
        val = compile_expr(stmt.value, builder, variables)
        ptr = builder.alloca(val.type, name=stmt.name)
        builder.store(val, ptr)
        variables[stmt.name] = ptr

    elif isinstance(stmt, FuncCall) and stmt.name == "print":
        for i, arg in enumerate(stmt.args):
            val = compile_expr(arg, builder, variables)

            if isinstance(arg, Constant) and isinstance(arg.value, str):
                str_ptr = create_global_string(module, builder, arg.value, f".str{i}")
                builder.call(puts_func, [str_ptr])
                builder.call(fflush_func, [ir.Constant(ir.PointerType(ir.IntType(8)), None)])

            elif isinstance(val, ir.Value) and val.type == ir.IntType(32):
                fmt_ptr = get_int_format_str(module, builder)
                builder.call(puts_func, [fmt_ptr, val])
    elif isinstance(stmt, ReturnValue) and return_modifier != "useless":
        val = compile_expr(stmt.value, builder, variables)
        builder.ret(val)

def compile_expr(expr, builder, variables):
    if isinstance(expr, Constant):
        val = expr.value
        if isinstance(val, int):
            return ir.Constant(ir.IntType(32), val)
        if isinstance(val, str):
            return val
    elif isinstance(expr, VariableRefrence):
        ptr = variables[expr.value]
        return builder.load(ptr, name=f"{expr.value}_val")
    elif isinstance(expr, BinaryOP):
        lhs = compile_expr(expr.left, builder, variables)
        rhs = compile_expr(expr.right, builder, variables)
        op = expr.operator

        if op == "+":
            return builder.add(lhs, rhs, name="addtmp")
        elif op == "-":
            return builder.sub(lhs, rhs, name="subtmp")
        elif op == "*":
            return builder.mul(lhs, rhs, name="multmp")
        elif op == "/":
            return builder.sdiv(lhs, rhs, name="divtmp")
        else:
            raise Exception(f"Unsupported operator: {op}")
    else:
        raise Exception(f"Unsupported expression: {expr}")


def execute_with_jit(module):
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()

    backing_mod = binding.parse_assembly(str(module))
    backing_mod.verify()

    engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    engine.finalize_object()
    engine.run_static_constructors()

    func_ptr = engine.get_function_address("main")

    import ctypes
    cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
    result = cfunc()

    print("\n")
    print(f"Finished with exit code: {result}")