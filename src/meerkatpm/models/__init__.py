from typing import Optional, List
from pydantic import BaseModel

class Module(BaseModel):
    name: str
    description: Optional[str]
    files: List[str]
    submodules: Optional[List['Module']]
    dependencies: Optional[List[str]]

class Project(BaseModel):
    name: str
    version: Optional[str]
    description: Optional[str]
    modules: Optional[List[Module]]
