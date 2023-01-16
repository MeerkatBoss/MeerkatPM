from typing import Optional, List, Literal
from pydantic import BaseModel

class Module(BaseModel):
    name: str
    description: Optional[str]
    files: List[str]
    submodules: List['Module'] = []
    dependencies: List[str] = []

class Project(BaseModel):
    name: str
    type: Literal['lib', 'exe']
    version: str
    author: Optional[str]
    author_email: Optional[str]
    description: Optional[str]
    files: List[str]
    modules: List[Module] = []
