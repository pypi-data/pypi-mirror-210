import importlib

from JsonQuery.errors import NoJsonParserModuleFound

def import_jsonquery_module(module_name: str):
    try:
        return importlib.import_module(module_name)
    except:
        raise NoJsonParserModuleFound(module_name)