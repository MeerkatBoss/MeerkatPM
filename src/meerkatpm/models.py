from typing import Optional, List, Literal

class Module:
    def __init__(self, *,
                name: str,
                headers: List[str] = [],
                sources: List[str],
                description: Optional[str] = None,
                submodules: List['Module'] = [],
                dependencies: List[str] = []) -> None:
        self.name = name
        self.description = description
        self.headers = headers
        self.sources = sources
        self.submodules = submodules
        self.dependencies = dependencies
        pass

    def find_submodule(self, name: str) -> Optional['Module']:
        module_name, _, submodule_path = name.partition('/')
        module = ([m for m in self.submodules if m.name == module_name] or [None])[0]
        if not module:
            return None
        if not submodule_path:
            return module
        return module.find_submodule(submodule_path)

    

class Project:
    def __init__(self, *,
                name: str,
                type: Literal['lib', 'exe'],
                version: str = '0.0.1',
                author: Optional[str] = None,
                author_email: Optional[str] = None,
                description: Optional[str] = None,
                headers: List[str] = [],
                sources: List[str],
                modules: List[Module] = []) -> None:
        self.name = name
        self.type = type
        self.version = version
        self.author = author
        self.author_email = author_email
        self.description = description
        self.headers = headers
        self.sources = sources
        self.modules = modules

    def find_module(self, name: str) -> Optional[Module]:
        module_name, _, submodule_path = name.partition('/')
        module = ([m for m in self.modules if m.name == module_name] or [None])[0]
        if not module:
            return None
        if not submodule_path:
            return module
        return module.find_submodule(submodule_path)
