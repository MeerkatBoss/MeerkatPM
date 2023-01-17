import os
from typing import Optional, List

from ruamel.yaml import YAML

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from meerkatpm.models import Project, Module
from meerkatpm.exceptions import UsageError
from meerkatpm.routers import Router

yaml = YAML()
yaml.register_class(Project)
yaml.register_class(Module)

class RouterDispatcher:
    routers: List[Router] = []
    project: Optional[Project] = None

    def __init__(self) -> None:
        if os.path.exists('manifest.yaml'):
            with open('manifest.yaml', 'r') as file:
                self.project = yaml.load(file)

    def add_router(self, router: Router) -> None:
        assert router.name not in [r.name for r in self.routers]
        self.routers.append(router)

    def run_program(self, argv: List[str]) -> None:
        if len(argv) < 2:
            print("Incorrect usage: not enough arguments")
            return

        cmd = argv[1]
        if cmd not in [r.name for r in self.routers]:
            print(f"Incorrect usage: unknown command '{cmd}'")
            return

        router = [r for r in self.routers if r.name == cmd][0]
        try:
            self.project = router.dispatch(argv[2], argv[3:], self.project)
        except UsageError as e:
            print(f"Incorrect usage of command '{cmd}': {e.args}")
            return
        
        with open('manifest.yaml', 'w') as file:
            yaml.dump(self.project, file)
