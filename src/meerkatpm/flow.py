import os
from typing import Optional, List
from pathlib import Path

from ruamel.yaml import YAML

from meerkatpm.models import Project, Module
from meerkatpm.exceptions import UsageError
from meerkatpm.routers import Router
from meerkatpm.codegen import get_module_cmake, get_project_cmake

yaml = YAML()
yaml.register_class(Project)
yaml.register_class(Module)

def update_module_cmake(module: Module, path: Path) -> None:
    with path.joinpath('CMakeLists.txt').open('w') as file:
        file.write(get_module_cmake(module))
    for m in module.submodules:
        update_module_cmake(m, path/m.name)

def update_project_files(project: Project) -> None:
    with open('manifest.yaml', 'w') as file:
        yaml.dump(project, file)
    src_path = Path('src/')
    for m in project.modules:
        update_module_cmake(m, src_path/m.name)

    with src_path.joinpath('CMakeLists.txt').open('w') as file:
        file.write(get_project_cmake(project))

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

        update_project_files(self.project)
