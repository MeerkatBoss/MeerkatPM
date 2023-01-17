import os
import shutil

from importlib.resources import read_text, path
from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error
from meerkatpm.models import Project
from meerkatpm.codegen import get_project_cmake

router = Router("project")

def init_folders() -> None:
    assert_error(not os.listdir(), "Project directory is not empty")
    os.mkdir('lib')
    os.mkdir('lib/include')
    os.mkdir('include')
    os.mkdir('src')
    os.mkdir('build')
    with path('meerkatpm.templates.cmake', 'run.cmake') as run_cmake:
        shutil.copy(run_cmake, os.getcwd())
    with path('meerkatpm.templates.cmake', 'cmake_uninstall.cmake') as uninstall_cmake:
        shutil.copy(uninstall_cmake, os.getcwd())


@router.handler("exe")
def project_exe(args: List[str], old_project: Optional[Project]) -> Project:
    assert_error(len(args) > 0, "Project name not specified")
    assert_error(len(args) == 1, "Too many arguments")
    assert_error(old_project is None, "Project already created")

    project = Project(name=args[0], type='exe', files=['main.cpp'])
    main = read_text('meerkatpm.templates.cpp', 'main.cpp').format(project_name=project.name)
    cmake_root = read_text('meerkatpm.templates.cmake', 'CMakeLists.txt').format(project_name=project.name)

    init_folders()
    with open('CMakeLists.txt', 'w') as file:
        file.write(cmake_root)
    with open('src/main.cpp', 'w') as file:
        file.write(main)
    with open('src/CMakeLists.txt', 'w') as file:
        file.write(get_project_cmake(project))

    return project
