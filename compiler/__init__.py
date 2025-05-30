from cgitb import strong

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
            string_elements = [ir.Constant(ir.IntType(8), len(string_value))]
            for c in string_value:
                string_elements.append(ir.Constant(ir.IntType(8), ord(c)))
            string_ptr = builder.call(backlight_scope["string_alloc"], string_elements)
            string = builder.call(backlight_scope["string_creator"], [string_ptr])
            return string
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
        arg_pretty = []
        if not scope[stmt.name].function_type.var_arg:
            for arg, param in zip(stmt.args, scope[stmt.name].function_type.args):
                evaluated = evaluate_expression(builder, arg, scope, loaded_vars)
                if param == ir.IntType(8).as_pointer() and evaluated.type != ir.IntType(8).as_pointer():
                    evaluated = builder.call(backlight_scope["string_content"], [evaluated])
                arg_pretty.append(evaluated)
        else:
            fc = scope[stmt.name]
            for i, a in enumerate(stmt.args):
                if i >= len(fc.function_type.args):
                    param = fc.function_type.args[len(fc.function_type.args) - 1]
                else:
                    param = fc.function_type.args[i]

                evaluated = evaluate_expression(builder, a, scope, loaded_vars)
                if param == ir.IntType(8).as_pointer() and evaluated.type == ir.IntType(32):
                    evaluated = builder.call(backlight_scope["num_string"], [evaluated])
                elif param == ir.IntType(8).as_pointer() and evaluated.type != ir.IntType(8).as_pointer():
                    evaluated = builder.call(backlight_scope["string_content"], [evaluated])

                arg_pretty.append(evaluated)
        if scope[stmt.name].function_type.var_arg:
            arg_pretty.append(ir.Constant(scope[stmt.name].function_type.args[0], None))
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
        if arg.tpe == "str":
            args.append(backlight_scope["string_struct"])
            continue
        args.append(types[arg.tpe])

    if stmt.return_type == "str":
        tpe = backlight_scope["string_struct"]
    else:
        tpe = types[stmt.return_type]

    header = ir.FunctionType(tpe, args)

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
            arg_pretty = []
            if not scope[inst.name].function_type.var_arg:
                for arg, param in zip(inst.args, scope[inst.name].function_type.args):
                    evaluated = evaluate_expression(func_builder, arg, scope, loaded_vars)
                    if param == ir.IntType(8).as_pointer() and evaluated.type == ir.IntType(32):
                        evaluated = func_builder.call(backlight_scope["num_string"], [evaluated])
                    elif param == ir.IntType(8).as_pointer() and evaluated.type != ir.IntType(8).as_pointer():
                        evaluated = func_builder.call(backlight_scope["string_content"], [evaluated])

                    arg_pretty.append(evaluated)
            else:
                fc = scope[inst.name]
                for i, a in enumerate(inst.args):
                    if i > len(fc.function_type.args):
                        param = fc.function_type.args[len(fc.function_type.args) - 1]
                    else:
                        param = fc.function_type.args[i]

                    evaluated = evaluate_expression(func_builder, a, scope, loaded_vars)
                    if param == ir.IntType(8).as_pointer() and evaluated.type == ir.IntType(32):
                        evaluated = func_builder.call(backlight_scope["num_string"], [evaluated])
                    elif param == ir.IntType(8).as_pointer() and evaluated.type != ir.IntType(8).as_pointer():
                        evaluated = func_builder.call(backlight_scope["string_content"], [evaluated])

                    arg_pretty.append(evaluated)
            if scope[inst.name].function_type.var_arg: arg_pretty.append(ir.Constant(scope[inst.name].function_type.args[0].type
                                                                                     , None))
            func_builder.call(scope[inst.name], arg_pretty)
            
    return func

backlight_scope = {}
def compile_code(ast):
    module = ir.Module(name="sparkle-program")

    global_scope = {}

    printf_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(8).as_pointer()])
    printf = ir.Function(module, printf_ty, name="__backlight_print")
    global_scope["print"] = printf

    backlight_string_struct = ir.global_context.get_identified_type("struct.BacklightString")
    backlight_string_ptr = backlight_string_struct.as_pointer()
    backlight_scope["string_struct"] = backlight_string_ptr

    backlight_str_createh = ir.FunctionType(backlight_string_ptr, [ir.IntType(8).as_pointer()])
    backlight_str_create = ir.Function(module, backlight_str_createh, name="__backlight_string_create")
    backlight_scope["string_creator"] = backlight_str_create

    backlight_str_lengthh = ir.FunctionType(ir.IntType(32), [backlight_string_ptr])
    backlight_str_length = ir.Function(module, backlight_str_lengthh, name="__backlight_string_length")
    backlight_scope["string_length"] = backlight_str_length
    global_scope["stuff"] = backlight_str_length

    backlight_string_alloch = ir.FunctionType(ir.IntType(8).as_pointer(), [ir.IntType(8)], var_arg=True)
    backlight_string_alloc = ir.Function(module, backlight_string_alloch, name="__backlight_generate_string_array")
    backlight_scope["string_alloc"] = backlight_string_alloc

    backlight_str_contenth = ir.FunctionType(ir.IntType(8).as_pointer(), [backlight_string_ptr])
    backlight_str_content = ir.Function(module, backlight_str_contenth, name="__backlight_string_content")
    backlight_scope["string_content"] = backlight_str_content

    backlight_str_formath = ir.FunctionType(backlight_string_ptr, [backlight_string_ptr], True)
    backlight_str_format = ir.Function(module, backlight_str_formath, "__backlight_string_format")
    backlight_scope["string_format"] = backlight_str_format
    global_scope["format"] = backlight_str_format

    backlight_num_strh = ir.FunctionType(ir.IntType(8).as_pointer(), [ir.IntType(32)])
    backlight_num_str = ir.Function(module, backlight_num_strh, name="__backlight_number_string")
    backlight_scope["num_string"] = backlight_num_str

    global_scope["str"] = backlight_num_str
    global_scope["strc"] = backlight_str_create


    malloc_ty = ir.FunctionType(ir.IntType(8).as_pointer(), [ir.IntType(64)])
    malloc = ir.Function(module, malloc_ty, name="malloc")
    global_scope["malloc"] = malloc


    for stmt in ast:
        if isinstance(stmt, FuncDeclr):
            func = parse_function_declaration(module, stmt, global_scope)
            global_scope[func.name] = func

    return module




def execute_with_jit(module):
    import ctypes as ct
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()

    backing_mod = binding.parse_assembly(str(module))
    backing_mod.verify()

    engine = binding.create_mcjit_compiler(backing_mod, target_machine)

    backlight_lib = ct.CDLL("compiler/backlight.dll")

    BacklightStringHandle = ct.c_void_p

    backlight_print = ct.cast(backlight_lib.__backlight_print, ct.c_void_p).value
    backlight_string_create = ct.cast(backlight_lib.__backlight_string_create, BacklightStringHandle).value
    backlight_string_length = ct.cast(backlight_lib.__backlight_string_length, BacklightStringHandle).value
    backlight_string_content = ct.cast(backlight_lib.__backlight_string_content, BacklightStringHandle).value
    backlight_number_string = ct.cast(backlight_lib.__backlight_number_string, BacklightStringHandle).value
    backlight_string_allocate = ct.cast(backlight_lib.__backlight_generate_string_array, BacklightStringHandle).value
    backlight_string_format = ct.cast(backlight_lib.__backlight_string_format, BacklightStringHandle).value


    engine.add_global_mapping(backing_mod.get_function("__backlight_print"), backlight_print)
    engine.add_global_mapping(backing_mod.get_function("__backlight_string_create"), backlight_string_create)
    engine.add_global_mapping(backing_mod.get_function("__backlight_string_length"), backlight_string_length)
    engine.add_global_mapping(backing_mod.get_function("__backlight_string_content"), backlight_string_content)
    engine.add_global_mapping(backing_mod.get_function("__backlight_number_string"), backlight_number_string)
    engine.add_global_mapping(backing_mod.get_function("__backlight_generate_string_array"), backlight_string_allocate)
    engine.add_global_mapping(backing_mod.get_function("__backlight_string_format"), backlight_string_format)

    engine.finalize_object()
    engine.run_static_constructors()

    return engine