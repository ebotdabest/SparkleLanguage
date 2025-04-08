from llvmlite import ir, binding
from parser.ltypes import *
from typing import Dict

types = {
    "int": ir.IntType(32),
    "double": ir.DoubleType()
}

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
        return ir.Constant(types[stmt.type], stmt.value)
    if isinstance(stmt, VariableRefrence):
        if scope[stmt.value] in loaded_vars:
            return loaded_vars[scope[stmt.value]]

        v = builder.load(scope[stmt.value])
        loaded_vars[scope[stmt.value]] = v
        return v
    if isinstance(stmt, UnaryOP):
        expr = evaluate_expression(builder, stmt.operand, scope)
        return builder.mul(expr, ir.Constant(expr.type, int(f"{stmt.operator}1")))
    if isinstance(stmt, FuncCall):
        arg_pretty = [evaluate_expression(builder, arg, scope, loaded_vars) for arg in stmt.args]
        cll = builder.call(scope[stmt.name], arg_pretty)
        return cll

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

    return func


def compile_code(ast):
    module = ir.Module(name="sparkle-program")

    global_scope = {}
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