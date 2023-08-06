from abc import ABC, abstractmethod


class InvokerValidationError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class InvokerField(ABC):
    name: str
    description: str

    @abstractmethod
    def validate(self):
        if self.name is None or len(self.name) == 0:
            raise InvokerValidationError("Name must exist")


class InvokerInputField(InvokerField):
    pass


def InvokerNetworkOutputBuilder():
    return None
