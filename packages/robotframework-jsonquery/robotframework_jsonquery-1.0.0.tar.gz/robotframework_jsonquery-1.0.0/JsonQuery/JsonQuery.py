"""Library for handling json queries using different backends
"""

import json
from types import ModuleType

from importlib import import_module

from JsonQuery.queries import JmesPath, JsonPathNg, Querable

jsonParserModule = {
    "jmespath": JmesPath,
    "jsonpath_ng.ext": JsonPathNg,
    "jsonpath_ng": JsonPathNg
}


class JsonQuery:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, query_module: str = "jmespath") -> None:
        self.imported_module: ModuleType = import_module(query_module)
        self.qmodule: Querable = jsonParserModule[query_module](self.imported_module)

    def get_query_module(self) -> str:
        """Get module name loaded on initialization

        Returns:
            str: module name, e.g. jmespath, jsonpath_ng.ext, jsonpath_ng
        """
        return f"{self.imported_module.__name__}"

    def read_json_file(self, file_path: str) -> dict:
        """Read json file

        Args:
            file_path (str): Path to json file, e.g. /tmp/some/file.json

        Returns:
            dict: file content in a dict format, ready to be parsed
        """
        with open(file_path, "r") as fl:
            content = json.load(fl)
        return content

    def query_json(self, document: dict, expression: str) -> dict:
        """Query json doucment/dictionary with a given expression using module of choice

        Args:
            document (dict): Content of a json file
            expression (str): expression used to query document using loaded module

        Returns:
            dict: expression result
        """
        result = self.qmodule.search(expression, document)
        return result
