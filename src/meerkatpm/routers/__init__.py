from typing import Callable, List, Dict, Optional

import meerkatpm.utils as utils
from meerkatpm.models import Project

RouteHandler = Callable[[List[str], Optional[Project]], Project]

class Router:
    name: str
    handlers: Dict[str, RouteHandler]

    def __init__(self, command: str) -> None:
        assert not utils.has_whitespace(command)
        
        self.name = command
        self.handlers = {}
        pass

    def handler(self, cmd: str):
        assert cmd not in self.handlers.keys()

        def decorator(func: RouteHandler):
            self.handlers[cmd] = func
            return func
        return decorator
    
    def dispatch(self, cmd: str, args: List[str], project: Optional[Project]) -> Project:
        utils.assert_error(
            cmd in self.handlers.keys(),
            f"Unknown '{self.name}' command: '{cmd}'"
        )

        return self.handlers[cmd](args, project)
