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
