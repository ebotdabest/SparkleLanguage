from llvmlite import ir, binding
from parser.ltypes import *
from typing import Dict

types = {
    "int": ir.IntType(32),
    "double": ir.DoubleType(),
    "str": ir.IntType(8).as_pointer()
}

def get_type_size(builder, typ):
    null_ptr = ir.Constant(typ.as_pointer(), None)
    gep = builder.gep(null_ptr, [ir.Constant(ir.IntType(32), 1)], inbounds=True)
    size = builder.ptrtoint(gep, ir.IntType(32))
    return size

def evaluate_expression(builder: ir.IRBuilder, stmt, scope, loaded_vars):
    if isinstance(stmt, BinaryOP):
        ls = evaluate_expression(builder, stmt.left, scope, loaded_vars)
        rs = evaluate_expression(builder, stmt.right, scope, loaded_vars)
        op = stmt.operator

        if op == "+": return builder.add(ls, rs)
        if op == "-": return builder.sub(ls, rs)
        if op == "*": return builder.mul(ls, rs)
        if op == "/": return builder.sdiv(ls, rs)

    if isinstance(stmt, Constant):
        if stmt.type == "str":
            string_value = stmt.value + "\0"
            # length = len(string_value)
            # char_type = ir.IntType(8)
            # array_type = ir.ArrayType(char_type, length)

            malloc_size = ir.Constant(ir.IntType(64), len(string_value))
            string_alloca = builder.call(scope["malloc"], [malloc_size])
            string_alloca.align = 1

            char_type = ir.IntType(8)
            for i, c in enumerate(string_value):
                ptr = builder.gep(string_alloca, [ir.Constant(ir.IntType(32), i)])
                builder.store(ir.Constant(char_type, ord(c)), ptr)


            # for i, c in enumerate(string_value):
            #     ptr = builder.gep(string_alloca, [
            #         ir.Constant(ir.IntType(32), 0),
            #         ir.Constant(ir.IntType(32), i)
            #     ])
            #     builder.store(ir.Constant(char_type, ord(c)), ptr)

            # string_ptr = builder.gep(string_alloca, [
            #     ir.Constant(ir.IntType(32), 0),
            #     ir.Constant(ir.IntType(32), 0)
            # ])
            return string_alloca

        return ir.Constant(types[stmt.type], stmt.value)
    if isinstance(stmt, VariableRefrence):
        if scope[stmt.value] in loaded_vars:
            return loaded_vars[scope[stmt.value]]

        v = builder.load(scope[stmt.value])
        loaded_vars[scope[stmt.value]] = v
        return v
    if isinstance(stmt, UnaryOP):
        expr = evaluate_expression(builder, stmt.operand, scope, loaded_vars)
        return builder.mul(expr, ir.Constant(expr.type, int(f"{stmt.operator}1")))
    if isinstance(stmt, FuncCall):
        arg_pretty = [evaluate_expression(builder, arg, scope, loaded_vars) for arg in stmt.args]
        cll = builder.call(scope[stmt.name], arg_pretty)
        return cll
    if isinstance(stmt, StringOP):
        lhs = evaluate_expression(builder, stmt.lhs, scope, loaded_vars)
        op = stmt.op
        rhs = evaluate_expression(builder, stmt.rhs, scope, loaded_vars)

        ll = builder.load(lhs)
        rl = builder.load(rhs)


        # builder.call(scope["malloc"], [ir.Constant(ir.IntType(64), len())])


def parse_function_declaration(module: ir.Module, stmt: FuncDeclr, global_scope):
    args = []
    for arg in stmt.args:
        args.append(types[arg.tpe])

    header = ir.FunctionType(types[stmt.return_type], args)

    func = ir.Function(module, header, name=stmt.name)
    func_builder = ir.IRBuilder(func.append_basic_block("entry"))

    scope = global_scope | {}
    for fa, ca in zip(func.args, stmt.args):
        ptr = func_builder.alloca(fa.type, name=fa.name + "_ptr")
        func_builder.store(fa, ptr)
        scope[ca.name] = ptr
        fa.name = ca.name

    loaded_vars = {}
    for inst in stmt.elements:
        if isinstance(inst, VarDeclr):
            expr = evaluate_expression(func_builder, inst.value, scope, loaded_vars)

            var = func_builder.alloca(expr.type, name=inst.name)
            scope[inst.name] = var
            func_builder.store(expr,var)
        elif isinstance(inst, ReturnValue):
            expr = evaluate_expression(func_builder, inst.value, scope, loaded_vars)
            func_builder.ret(expr)
        elif isinstance(inst, ReassignVariable):
            expr = evaluate_expression(func_builder, inst.value, scope, loaded_vars)
            func_builder.store(expr,scope[inst.var])
        elif isinstance(inst, FuncCall):
            arg_pretty = [evaluate_expression(func_builder, arg, scope, loaded_vars) for arg in inst.args]
            func_builder.call(scope[inst.name], arg_pretty)
            
    return func


def compile_code(ast):
    module = ir.Module(name="sparkle-program")

    global_scope = {}

    printf_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
    printf = ir.Function(module, printf_ty, name="printf")
    global_scope["print"] = printf

    malloc_ty = ir.FunctionType(ir.IntType(8).as_pointer(), [ir.IntType(64)])
    malloc = ir.Function(module, malloc_ty, name="malloc")
    global_scope["malloc"] = malloc


    for stmt in ast:
        if isinstance(stmt, FuncDeclr):
            func = parse_function_declaration(module, stmt, global_scope)
            global_scope[func.name] = func

    return module


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

    return engine