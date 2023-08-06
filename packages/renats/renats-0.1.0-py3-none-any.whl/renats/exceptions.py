class InvalidDataFormat(ValueError):
    def __init__(self, message: str, data):
        super().__init__(message)
        self.data = data


class NatsClientError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


class RequestMethodError(Exception):
    def __init__(self, status: int, error: str):
        super().__init__(f"{status}: {error}")
        self.status: int = status
        self.error: str = error
