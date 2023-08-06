from .inputbase import InvokerNetworkInputBase


class InvokerNetworkTextInput(InvokerNetworkInputBase):
    def __init__(
        self,
        description: str = None,
        required: bool = False,
        minChar: int = None,
        maxChar: int = None,
        textarea: bool = False,
    ):
        super().__init__(description, required)
        if minChar is None:
            self.minchar = -1
        else:
            if not isinstance(minChar, int) or minChar < 0:
                raise ValueError("Invalid Value for {}".format("min char"))
            self.minchar = minChar
        if maxChar is None:
            self.maxchar = -1
        else:
            if not isinstance(maxChar, int) or maxChar < 0:
                raise ValueError("Invalid Value for {}".format("max char"))
            self.maxchar = maxChar
        self.textarea = textarea
        self.type = "text"
