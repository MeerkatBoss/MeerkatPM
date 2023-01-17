from typing import Optional, List, Literal

class Module:
    name: str
    description: Optional[str]
    files: List[str]
    submodules: List['Module'] = []
    dependencies: List[str] = []

class Project:
    name: str
    type: Literal['lib', 'exe']
    version: str = '0.0.1'
    author: Optional[str] = None
    author_email: Optional[str] = None
    description: Optional[str] = None
    files: List[str]
    modules: List[Module] = []
    def __init__(self, *,
                name: str,
                type: Literal['lib', 'exe'],
                version: str = '0.0.1',
                author: Optional[str] = None,
                author_email: Optional[str] = None,
                description: Optional[str] = None,
                files: List[str],
                modules: List[Module] = []) -> None:
        self.name = name
        self.type = type
        self.version = version
        self.author = author
        self.author_email = author_email
        self.description = description
        self.files = files
        self.modules = modules
