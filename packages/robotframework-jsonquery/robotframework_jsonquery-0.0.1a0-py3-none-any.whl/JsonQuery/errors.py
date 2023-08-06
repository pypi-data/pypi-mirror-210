class Error(Exception):
    ...

class NoJsonParserModuleFound(Error):
    def __init__(self, module_name, *args):
        self.module_name = module_name
        super().__init__(self.module_name, *args)
    
    