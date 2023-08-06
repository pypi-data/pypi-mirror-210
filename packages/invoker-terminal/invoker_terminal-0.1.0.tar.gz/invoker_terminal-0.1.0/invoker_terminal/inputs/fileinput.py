from .inputbase import InvokerNetworkInputBase


class InvokerNetworkFileInput(InvokerNetworkInputBase):
    def __init__(self, description: str = None, required: bool = False):
        super().__init__(description, required)
        self.type = "file"
