import ast
import importlib
import json
import logging
import os
import sys
from typing import List

INVOKER_DECORATOR = "invoker"
INVOKER_INPUT = "invoker_input"
INVOKER_NETWORK_INPUT = "InvokerNetworkInput"
INVOKER_INPUT_NAME = "name"
INVOKER_INPUT_DESC = "description"
ALLOWED_KEYWORDS = [INVOKER_INPUT_NAME, INVOKER_INPUT_DESC]


def model_check():
    logging.info("checking model inputs/outputs")
    f = open("./model.py", "r")
    root = ast.parse(f.read(), "model.py")
    f.close()
    # only one function with @invoker decorator
    invokerDecoratorCount = 0
    invokerFunction: ast.FunctionDef = None
    invokerInputDecoratorCount = 0
    invokerInputClass: ast.ClassDef = None
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.FunctionDef):
            decorators = node.decorator_list
            for decorator in decorators:
                if isinstance(decorator, ast.Call):
                    if decorator.func.id == INVOKER_DECORATOR:
                        invokerDecoratorCount += 1
                        invokerFunction = node
                if (
                    isinstance(decorator, ast.Name)
                    and decorator.id == INVOKER_DECORATOR
                ):
                    invokerDecoratorCount += 1
                    invokerFunction = node

        if isinstance(node, ast.ClassDef):
            decorators = node.decorator_list
            for decorator in decorators:
                if decorator.id == INVOKER_INPUT:
                    invokerInputDecoratorCount += 1
                    invokerInputClass = node

    if not invokerInputDecoratorCount == 1:
        logging.info(
            "Model needs to have @invoker_input decorator to an input class"
        )
        os._exit(1)

    if not invokerDecoratorCount == 1:
        logging.info("Model can have only one @invoker decorator")
        os._exit(1)

    arguments: ast.arguments = invokerFunction.args
    args: List[ast.arg] = arguments.args
    if not len(args) == 1:
        logging.info("Invoker function should have only one input")
        os._exit(1)

    # make sure input passed to the invoker function
    # is actually invokerInputClass
    desc = {}
    print(ast.dump(invokerInputClass))
    spec = importlib.util.spec_from_file_location(
        "model", os.path.abspath("./model.py")
    )
    foo = importlib.util.module_from_spec(spec)
    sys.modules["model"] = foo
    spec.loader.exec_module(foo)
    cls = getattr(foo, invokerInputClass.name)
    obj = cls()
    inputs = obj.toJSON()
    desc.update(inputs)
    print(ast.dump(invokerFunction))
    decorator_list = invokerFunction.decorator_list
    for decorator in decorator_list:
        if isinstance(decorator, ast.Call):
            keywords = decorator.keywords
            for keyword in keywords:
                if keyword.arg in ALLOWED_KEYWORDS:
                    val: ast.Constant = keyword.value
                    desc[keyword.arg] = val.value
    jsonformatted = json.dumps(desc, sort_keys=True, indent=4)
    f = open("./desc.json", "w")
    f.write(jsonformatted)
    f.close()
    print(jsonformatted)
    logging.info("Success")
