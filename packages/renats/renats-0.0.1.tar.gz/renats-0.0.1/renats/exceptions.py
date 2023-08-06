from typing import Any


class InvalidPayloadData(ValueError):
    def __init__(self, message: str, data: bytes | dict[str, Any]):
        super().__init__(message)
        self.data: bytes | Any = data


class NatsClientError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


class NoResponders(NatsClientError):
    pass
