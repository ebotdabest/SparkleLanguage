from llvmlite import ir, binding
from parser.ltypes import *

types = {
    "int": ir.IntType
}

def compile_code(ast):
    module = ir.Module(name="program")
    scope_type = ir.FunctionType(ir.VoidType(), [])
    scope_func = ir.Function(module, scope_type, "scope")
    scope_block = scope_func.append_basic_block(name="entry")
    scope_builder = ir.IRBuilder(scope_block)

    scope_builder.ret_void()

    puts_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=False)
    puts_func = ir.Function(module, puts_ty, name="puts")

    fflush_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))])
    fflush = ir.Function(module, fflush_ty, name="fflush")

    variables = {}

    for a in ast:
        if isinstance(a, FuncDeclr):
            args = []
            for _ in a.args:
                args.append(ir.IntType(32))
            func_type = ir.FunctionType(types[a.return_type](32), args)
            func = ir.Function(module, func_type, name=a.name)
            block = func.append_basic_block("entry")
            builder = ir.IRBuilder(block)

            for i1,e in enumerate(a.elements):
                if isinstance(e, VarDeclr):
                    if isinstance(e.value, Constant):
                        tpe = str(type(e.value.value)).replace("<class '", "").replace("'>",
                                                                                       "")

                        ptr = builder.alloca(types[tpe](32), name=e.name)
                        builder.store(ir.Constant(types[tpe](32), e.value.value), ptr)

                        val = builder.load(ptr, name=e.name)
                        variables[e.name] = val


                elif isinstance(e, FuncCall):
                    if e.name == "print":
                        formatted_args = []
                        for i, ar in enumerate(e.args):
                            if isinstance(ar, Constant):
                                if type(ar.value) == str:
                                    str_val = bytearray(ar.value, "utf8")
                                    str_type = ir.ArrayType(ir.IntType(8), len(str_val))
                                    const_str = ir.Constant(str_type, [ir.IntType(8)(b) for b in str_val])

                                    str_global = ir.GlobalVariable(module, str_type, name=f".str{i1}{i}")
                                    str_global.linkage = "internal"
                                    str_global.global_constant = True
                                    str_global.initializer = const_str
                                    str_global.unnamed_addr = True

                                    zero = ir.Constant(ir.IntType(32), 0)
                                    str_ptr = builder.gep(str_global, [zero, zero])
                                    formatted_args.append(str_ptr)

                        for fa in formatted_args:
                            builder.call(puts_func, [fa])
                            null_ptr = ir.Constant(ir.PointerType(ir.IntType(8)), None)
                            builder.call(fflush, [null_ptr])
                if isinstance(e, ReturnValue):
                    if isinstance(e.value, Constant):
                        builder.ret(ir.Constant(ir.IntType(32), e.value.value))
                    elif isinstance(e.value, VariableRefrence):
                        val_ptr = variables[e.value.value]
                        if isinstance(val_ptr, ir.AllocaInstr):
                            val = builder.load(val_ptr, name=f"{e.value.value}_val")
                        else:
                            val = val_ptr
                        builder.ret(val)

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

    func_ptr = engine.get_function_address("main")

    import ctypes
    cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
    result = cfunc()

    print()
    print(f"Finished with exit code: {result}")