from .inputbase import InvokerNetworkInputBase


class InvokerNetworkSelectInput(InvokerNetworkInputBase):
    def __init__(
        self,
        description: str = None,
        required: bool = False,
        options: list[str] = [],
    ):
        super().__init__(description, required)
        if len(options) == 0:
            raise ValueError("Options cannot be empty")
        self.type = "select"
        self.options = options
