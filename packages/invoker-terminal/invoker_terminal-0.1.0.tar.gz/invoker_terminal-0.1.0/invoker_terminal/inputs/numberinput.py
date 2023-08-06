from .inputbase import InvokerNetworkInputBase


class InvokerNetworkNumberInput(InvokerNetworkInputBase):
    def __init__(
        self,
        description: str = None,
        required: bool = False,
        minNum: int = None,
        maxNum: int = None,
    ):
        super().__init__(description, required)
        if not minNum is None:
            if not isinstance(minNum, int):
                raise ValueError(
                    "Invalid value for minNum expected int got {} instead".format(
                        minNum
                    )
                )
            else:
                self.minnum = minNum
        if not maxNum is None:
            if not isinstance(maxNum, int):
                raise ValueError(
                    "Invalid value for maxNum expected int got {} instead".format(
                        maxNum
                    )
                )
            else:
                self.maxnum = maxNum
        self.type = "number"
