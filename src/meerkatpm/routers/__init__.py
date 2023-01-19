from typing import Callable, List, Dict, Optional

import meerkatpm.utils as utils
from meerkatpm.models import Project

RouteHandler = Callable[[List[str], Optional[Project]], Project]

class Router:
    def __init__(self, command: str) -> None:
        assert not utils.has_whitespace(command)
        
        self.name = command
        self.handlers: Dict[str, RouteHandler] = {}
        self.empty_handler =\
            lambda *_: utils.assert_error(False, f"Cannot invoke '{self.name}' command without parameter")
        pass

    def handler(self, cmd: str):
        assert cmd not in self.handlers.keys()

        def decorator(func: RouteHandler):
            self.handlers[cmd] = func
            return func
        return decorator
    
    def default_handler(self, func: RouteHandler):
        self.empty_handler = func
        return func
    
    def dispatch(self, cmd: str, args: List[str], project: Optional[Project]) -> Project:
        utils.assert_error(
            cmd in self.handlers.keys(),
            f"Unknown '{self.name}' command: '{cmd}'"
        )

        return self.handlers[cmd](args, project)
