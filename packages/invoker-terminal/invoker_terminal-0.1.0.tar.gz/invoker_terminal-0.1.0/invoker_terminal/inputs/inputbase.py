import json


class InvokerNetworkInputBase:
    def __init__(self, description: str = None, required: bool = False):
        self.name = None
        if description is None:
            self.description = ""
        else:
            self.description = description
        self.required = required

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )

    def setName(self, name):
        self.name = name
