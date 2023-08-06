from _typeshed import Incomplete

class HttpException(Exception):
    status: Incomplete
    def __init__(self, status: int = ...) -> None: ...
