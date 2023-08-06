import importlib
import os
import sys

from invoker_terminal import InvokerOutput, ParseInput


def cmd_invoke(config, args):
    spec = importlib.util.spec_from_file_location(
        "model", os.path.abspath("./model.py")
    )
    foo = importlib.util.module_from_spec(spec)
    sys.modules["model"] = foo
    spec.loader.exec_module(foo)
    fn = getattr(foo, "invoke")
    print(fn)
    dummy = ParseInput()
    run = fn(dummy)
    print(run)
    InvokerOutput.done()
