from typing import Callable, List, Dict

import meerkatpm.utils as utils

class Router:
    name: str
    handlers: Dict[str, Callable[[List[str]], None]]

    def __init__(self, command: str) -> None:
        utils.assert_raise(
            not utils.has_whitespace(command),
            "Command name cannot contain whitespace characters.")
        
        self.name = command
        self.handlers = {}
        pass

    def handler(self, cmd: str):
        utils.assert_raise(
            cmd not in self.handlers.keys(),
            f"'{cmd}' command already registered for '{self.name}' handler"
        )

        def decorator(func: Callable):
            self.handlers[cmd] = func
            return func
        return decorator
    
    def dispatch(self, cmd: str, args: List[str]) -> None:
        utils.assert_error(
            cmd in self.handlers.keys(),
            f"Unknown '{self.name}' command: '{cmd}'"
        )

        self.handlers[cmd](args)
        pass

class RouterDispatcher:
    routers: List[Router]

    def __init__(self) -> None:
        self.routers = []
        pass

    def add_router(self, router: Router) -> None:
        utils.assert_raise(
            router.name not in [r.name for r in self.routers],
            f"Duplicate router '{router.name}'"
        )
        self.routers.append(router)

    def dispatch(self, cmd: str, args: List[str]) -> None:
        utils.assert_error(
            cmd in [r.name for r in self.routers],
            f"Unknown command: '{cmd}'"
        )
        utils.assert_error(
            len(args) > 0,
            f"No arguments for command given"
        )

        router = [r for r in self.routers if r.name == cmd][0]
        router.dispatch(args[0], args[1:])
        pass
        
    