#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import os
import jinja2
import re
from collections import namedtuple
import subprocess
import sys
from jinja2 import Environment, FileSystemLoader, Template
from template.plugin_impl import IMPL

try:
    # use faster C loader if available
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def parse_native_yaml(path):
    with open(path, "r", encoding='UTF-8') as f:
        return yaml.load(f, Loader=Loader)


class Shell(object):
    @staticmethod
    def run(shell):
        try:
            command = ['bash', '-c', shell]
            process = subprocess.Popen(
                command, stdout=sys.stdout, stderr=sys.stderr)
            err = process.wait()
        except subprocess.CalledProcessError as e:
            err = e.returncode
        return err


def jinja2_render(tpl_file, params, render_file):
    loader = os.path.dirname(tpl_file)
    tpl_basename = os.path.basename(tpl_file)
    env = Environment(loader=FileSystemLoader(loader))
    tpl = env.get_template(tpl_basename)

    with open(render_file, "wb") as fout:
        render_content = tpl.render(render=params)
        fout.write(render_content.encode("utf-8"))


def to_snake(name):
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()


def gen_check_input_arg_template(arg_type, arg):
    template = Template(
        r"""
        if {{arg}} is not None and not isinstance({{arg}}, {{arg_type}}):
            raise AIEError(AIEErrorCode.ARGS_ERROR, f"{{arg}} 只支持{{arg_type}}类型参数, 传入类型为{type({{arg}})}")
    """
    )
    return template.render(arg=arg, arg_type=arg_type)


TYPE_DEF = dict()


def decl_type(arg_type, returns_type=False):
    arg_types = arg_type.split('|')
    if len(arg_types) == 0:
        raise Exception(f"arg_type 不能为空")

    if len(arg_types) == 1:
        if arg_types[0] in TYPE_DEF:
            if returns_type and arg_types[0] in ("int", "float", "bool", "str", "list", "tuple", "dict", "object"):
                return ("object", "object")
            elif arg_types[0] == "float" and not returns_type:
                return ("[int,float]", "(int,float)")
            else:
                return (TYPE_DEF[arg_types[0]], TYPE_DEF[arg_types[0]])
        else:
            raise Exception(f"arg_type: {arg_type} not support")

    union_named_type = "Union["
    parenthesis_named_type = "("
    for i in range(len(arg_types)):
        if arg_types[i] in TYPE_DEF:
            if returns_type and arg_types[i] in ("int", "float", "bool", "str", "list", "tuple", "dict", "object"):
                union_named_type = union_named_type + "object"
                parenthesis_named_type = parenthesis_named_type + "object"
            elif arg_types[i] == "float" and not returns_type:
                union_named_type = union_named_type + "int,float"
                parenthesis_named_type = parenthesis_named_type + "int,float"
            else:
                union_named_type = union_named_type + TYPE_DEF[arg_types[i]]
                parenthesis_named_type = parenthesis_named_type + \
                    TYPE_DEF[arg_types[i]]
        else:
            raise Exception(
                f"arg_type: {arg_type}. type {arg_types[i]} not support")

        if i != len(arg_types) - 1:
            union_named_type = union_named_type + ","
            parenthesis_named_type = parenthesis_named_type + ","
    union_named_type = union_named_type + "]"
    parenthesis_named_type = parenthesis_named_type + ")"
    return (union_named_type, parenthesis_named_type)


def gen_input_args(args, sig_type):
    if sig_type == "__init__" or sig_type == "self":
        input_args = "self"
    elif sig_type == "staticmethod":
        input_args = ""
    elif sig_type == "override":
        input_args = "self"
    elif sig_type == "abstractmethod":
        input_args = "self"
    else:
        raise Exception(f"sig_type {sig_type} not support")

    for arg in args:
        if arg.bind_arg is None or arg.bind_arg != "self":
            input_arg = arg.name + ":" + decl_type(arg.type)[0]
            if input_args != "":
                input_args = input_args + ", "
            input_args = input_args + input_arg

            if arg.default is not None:
                input_args = input_args + " = " + arg.default

    return input_args


def gen_override_args(args):
    input_args = ""
    for arg in args:
        if arg.bind_arg is None or arg.bind_arg != "self":
            input_arg = arg.name
            if input_args != "":
                input_args = input_args + ", "
            input_args = input_args + input_arg

            if arg.default is not None:
                input_args = input_args + " = " + arg.default

    return input_args


def gen_invoke_args(args):
    invoke_args = dict()
    for arg in args:
        if len(arg) < 3 or arg[2] != "self":
            invoke_args[arg[1]] = arg[1]
        else:
            invoke_args[arg[1]] = "self"
    return invoke_args


def convert_arg(func_arg):
    Arg = namedtuple(
        "Arg", "type name bind_arg default"
    )

    arg_type, arg = func_arg.split(' ')
    if arg_type == "" or arg == "":
        raise Exception(f"func_arg: {func_arg} 缺少arg_type、arg")
    start_colon = arg.find(':')
    start_equal = arg.find('=')
    if start_colon != -1 and start_equal != -1:
        if start_colon > start_equal:
            raise Exception(f'{func_arg}, 参数:应该在=前, eg: Image mask:self=null')

    arg_name_end = len(arg)
    if start_colon != -1:
        arg_name_end = start_colon
    elif start_equal != -1:
        arg_name_end = start_equal
    arg_name = arg[:arg_name_end]

    bind_arg = None
    if start_colon != -1:
        bind_arg_end = len(arg)
        if start_equal != -1:
            bind_arg_end = start_equal
        bind_arg = arg[start_colon+1:bind_arg_end]

    default = None
    if start_equal != -1:
        default = arg[start_equal+1:]

    return Arg(arg_type, arg_name, bind_arg, default)


def gen_check_invoke_arg_template(arg):
    template = Template(
        r"""
        if "{{arg}}" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数{{arg}}不能为空")
    """
    )
    return template.render(arg=arg)

def parse_function(kclass, signature):
    Func = namedtuple(
        "Func", "impl annotation func_def func_invoke sig_type input_args check_input_args invoke_args override_args check_invoke_args returns"
    )

    if "plugin_impl" in signature:
        if not signature["plugin_impl"] in IMPL:
            raise Exception(
                f'plugin_impl: {signature["plugin_impl"]} 在 template/plugin_impl 中没有实现')
        impl = IMPL[signature["plugin_impl"]]
        return Func(impl, None, None, None, None, None, None, None, None, None, None)

    func_splited = signature["func"].split("->")
    if len(func_splited) != 2:
        raise Exception(f"func signature {signature['func']} 缺少返回值")
    func, returns = func_splited[0], func_splited[1].strip()
    if returns == "":
        raise Exception(f"func {func} 缺少返回值")
    returns_type = decl_type(returns, True)[0]
    args_start = func.find("(")
    args_end = func.rfind(")")
    args_str = func[args_start + 1: args_end]
    func_invoke = func[:args_start].strip()

    args = [convert_arg(arg.strip())
            for arg in args_str.split(",") if args_str != ""]

    sig_type = "self"
    if "type" in signature:
        sig_type = signature["type"].strip()
    func_def = func_invoke
    if sig_type == "__init__":
        func_def = "__init__"
    if "func_def_alias" in signature:
        func_def = signature["func_def_alias"]

    input_args = gen_input_args(args, sig_type)
    check_input_args = [
        gen_check_input_arg_template(decl_type(arg.type)[1], arg.name)
        for arg in args if arg.bind_arg is None or arg.bind_arg != "self"
    ]
    invoke_args = gen_invoke_args(args)

    check_invoke_args = [
        gen_check_invoke_arg_template(arg.name)
        for arg in args if (arg.bind_arg is None or arg.bind_arg != "self") and arg.default is None
    ]

    func_invoke = kclass + '.' + func_invoke
    if "func_invoke_alias" in signature:
        func_invoke = signature["func_invoke_alias"]

    annotation = None
    if sig_type == "__init__" or sig_type == "self" or sig_type == "override":
        pass
    elif sig_type == "staticmethod":
        annotation = "@staticmethod"
    elif sig_type == "abstractmethod":
        annotation == "@abc.abstractmethod"
    else:
        raise Exception(f"sig_type {sig_type} not support")

    override_args = None
    if sig_type == "override":
        override_args = gen_override_args(args)

    return Func(
        None,
        annotation,
        func_def,
        func_invoke,
        sig_type,
        input_args,
        check_input_args,
        invoke_args,
        override_args,
        check_invoke_args,
        returns_type,
    )


def reformat(file):
    shell = f'black {file}'
    err = Shell.run(shell)
    if err != 0:
        raise Exception(f"file: {file} reformat error")


def generate_aie_object_code(source_path, declarations):
    for name, signatures in declarations.items():
        params = dict()
        parent_kclass_start = name.find("(")
        parent_kclass_end = name.find(")")
        if parent_kclass_start != -1 or parent_kclass_end != -1:
            parent_kclass = name[parent_kclass_start + 1: parent_kclass_end]
            if parent_kclass == "":
                raise Exception(f"{name} 父类解析为空")
            params["parent_kclass"] = decl_type(parent_kclass, True)[1]
            kclass = name[:parent_kclass_start]
        else:
            params["parent_kclass"] = "FunctionNode"
            kclass = name

        params["kclass"] = kclass
        params["funcs"] = [parse_function(kclass,
                                          signature) for signature in signatures]

        tpl_file = source_path + "/template/aie_object.template"
        # render_file = source_path + "/aie_object/" + \
        #     to_snake(kclass) + "_gen.py"
        render_file = source_path + "/aie_object/" + \
            to_snake(kclass) + ".py"
        jinja2_render(tpl_file, params, render_file)
        reformat(render_file)


def generate_module_init_code(source_path, declarations):
    import_decls = list()
    for name, signatures in declarations.items():
        parent_kclass_start = name.find("(")
        if parent_kclass_start != -1:
            kclass = name[:parent_kclass_start]
        else:
            kclass = name
        # module_file = to_snake(kclass) + "_gen"
        module_file = to_snake(kclass)
        import_decls.append("from aie.aie_object." +
                            module_file + " import " + kclass)

    params = {"import_decls": import_decls}

    tpl_file = source_path + "/template/__init__.template"
    render_file = source_path + "/__init__.py"
    jinja2_render(tpl_file, params, render_file)
    reformat(render_file)


def main():
    source_path = os.path.dirname(os.path.abspath(__file__))
    global TYPE_DEF
    TYPE_DEF = parse_native_yaml(source_path + "/type_def.yaml")
    declarations = parse_native_yaml(source_path + "/functions.yaml")
    print(TYPE_DEF)
    print(declarations)
    generate_aie_object_code(source_path, declarations)
    generate_module_init_code(source_path, declarations)


if __name__ == "__main__":
    main()
