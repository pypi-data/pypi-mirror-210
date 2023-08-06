class ModuleUser:
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.is_authenticated = True
        self.is_interconnected_module = True
