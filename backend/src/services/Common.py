import json
from .Utils import init_by_json


class HTTPRequest:
    def __init__(self, init=None) -> None:
        init_by_json(self, init)


class HTTPResponse:
    status = 200
    data = {}
    error_data = ""
    error_code = 0

    def __init__(self, init=None) -> None:
        if init is not None:
            init_by_json(self, init)
        else:
            self.status = 200
            self.data = {}
            self.error_data = ""


class GeneralObject:
    def __init__(self) -> None:
        pass
