from .inputbase import InvokerNetworkInputBase


class InvokerNetworkRangeInput(InvokerNetworkInputBase):
    def __init__(
        self,
        description: str = None,
        required: bool = False,
        min: int = None,
        max: int = None,
        step: int = None,
    ):
        super().__init__(description, required)
        self.type = "range"
        if min is None:
            self.min = -1
        if max is None:
            self.max = -1
        if step is None:
            self.step = -1
        self.min = min
        self.max = max
        self.step = step
