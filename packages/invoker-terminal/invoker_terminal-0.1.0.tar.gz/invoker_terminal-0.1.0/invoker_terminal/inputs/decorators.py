import importlib
import inspect
import json

from .inputbase import InvokerNetworkInputBase


def invoker(name: str = None, tags: list[str] = [], description: str = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print("pre invoker wapper")
            res = func(*args, **kwargs)
            print("post invoker wrapper")
            return res

        return wrapper

    return decorator


def invoker_input(cls):
    def wrap(cls):
        return _process_class(cls)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)


def _process_class(cls):
    cls_annotations = cls.__dict__.get("__annotations__", {})
    annotations = cls_annotations.items()
    for name, type in annotations:
        # all annotatioins must inherit from InvokerNetworkInputBase
        if not issubclass(type, InvokerNetworkInputBase):
            raise TypeError(
                "Attribute '{attribute}' having {child} type needs to inherit from {parent}. Please use Invoker Network Input types only".format(
                    attribute=name,
                    child=type.__name__,
                    parent=InvokerNetworkInputBase.__name__,
                )
            )
        member = getattr(cls, name, None)
        if member is None:
            print(type)
            print("member is none init please {}, {}".format(name, type))
            setattr(cls, name, type())

    attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    members = list(
        filter(
            (lambda a: not (a[0].startswith("__") and a[0].endswith("__"))),
            attributes,
        )
    )
    for name, obj in members:
        if not issubclass(obj.__class__, InvokerNetworkInputBase):
            raise ValueError(
                "Expecting Invoker Network Input type for '{attribute}' but got {wrongtype}".format(
                    attribute=name, wrongtype=obj.__class__.__name__
                )
            )
        obj.setName(name)

    def toJSON(self):
        attributes = inspect.getmembers(
            self, lambda a: not (inspect.isroutine(a))
        )
        members = list(
            filter(
                (
                    lambda a: not (
                        a[0].startswith("__") and a[0].endswith("__")
                    )
                ),
                attributes,
            )
        )
        ret = {}
        ret["inputs"] = []
        for name, obj in members:
            ret["inputs"].append(obj.__dict__)
        return ret

    # inject toSON
    cls.toJSON = toJSON

    return cls
