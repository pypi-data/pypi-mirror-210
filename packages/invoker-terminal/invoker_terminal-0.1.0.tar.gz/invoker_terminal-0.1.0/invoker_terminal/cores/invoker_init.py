import json
import zipfile

from ..inputs.numberinput import InvokerNetworkNumberInput
from ..inputs.textinput import InvokerNetworkTextInput


def Invoker_init():
    print("invoker init here for containers")
    pass


class dummyObj(object):
    pass


# parse the input.zip file
# then populate the object accordingly
def ParseInput(path=None):
    if path is None:
        path = "/invoker/input.zip"
    archive = zipfile.ZipFile(path, "r")
    inputdata = archive.read("input/desc.json").decode("utf-8")
    dummy = dummyObj()
    parsed = json.loads(inputdata)
    # validate the input here
    for key in parsed:
        val = parsed[key]
        if val == "@@linked":
            file = archive.read("input/files/{}".format(key))
            setattr(dummy, key, file)
        else:
            setattr(dummy, key, val)
    return dummy
