from types import ModuleType
from typing import Protocol, Union


class Querable(Protocol):
    def search(self, expression: str, document: dict) -> Union[list, dict]:
        ...


class JmesPath:
    def __init__(self, module: ModuleType):
        self.module_type = module

    def search(self, expression: str, document: dict) -> Union[list, dict]:
        return self.module_type.search(expression, document)


class JsonPathNg:
    def __init__(self, module: ModuleType):
        self.module_type = module

    def search(self, expression: str, document: dict) -> Union[list, dict]:
        jsng_expr = self.module_type.parse(expression)
        return [result.value for result in jsng_expr.find(document)]
