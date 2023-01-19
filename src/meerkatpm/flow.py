import os
import subprocess
from typing import Optional, List
from pathlib import Path

from ruamel.yaml import YAML

from meerkatpm.models import Project, Module
from meerkatpm.exceptions import UsageError
from meerkatpm.routers import Router
from meerkatpm.codegen import get_module_cmake, get_project_cmake
from meerkatpm.utils import progress_report

yaml = YAML()
yaml.register_class(Project)
yaml.register_class(Module)

def update_module_cmake(module: Module, path: Path) -> None:
    with path.joinpath('CMakeLists.txt').open('w') as file:
        file.write(get_module_cmake(module))
    for m in module.submodules:
        update_module_cmake(m, path/m.name)

@progress_report("Updating project files")
def update_project_files(project: Project) -> None:
    with open('manifest.yaml', 'w') as file:
        yaml.dump(project, file)
    src_path = Path('src/')
    for m in project.modules:
        update_module_cmake(m, src_path/m.name)

    with src_path.joinpath('CMakeLists.txt').open('w') as file:
        file.write(get_project_cmake(project))

@progress_report("Running cmake")
def run_cmake() -> None:
    subprocess.run(['cmake', '-S.', '-Bbuild/Debug', '-DCMAKE_BUILD_TYPE=Debug'], stdout=subprocess.DEVNULL)
    subprocess.run(['cmake', '-S.', '-Bbuild/Release', '-DCMAKE_BUILD_TYPE=Release'], stdout=subprocess.DEVNULL)


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
        if len(argv) < 1:
            print("Incorrect usage: no arguments")
            return
        
        argv = argv[1:]

        cmd = argv[0]
        if cmd not in [r.name for r in self.routers]:
            print(f"Incorrect usage: unknown command '{cmd}'")
            return

        router = [r for r in self.routers if r.name == cmd][0]
        try:
            if len(argv) >= 2 and router.has_handler(argv[1]):
                self.project = router.dispatch(argv[1], argv[2:], self.project)
            else:
                self.project = router.empty_handler(argv[1:], self.project)
        except UsageError as e:
            print(f"Incorrect usage of command '{cmd}': {e.args[0]}")
            return

        update_project_files(self.project)
        run_cmake()
