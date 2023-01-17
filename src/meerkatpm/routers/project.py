import os
import shutil
import datetime

from importlib.resources import read_text, path
from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error
from meerkatpm.models import Project

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
    init_folders()

    project = Project(name=args[0], type='exe', files=['main.cpp'])
    cmake_root = read_text('meerkatpm.templates.cmake', 'CMakeLists.txt').format(project_name=project.name)
    main = read_text('meerkatpm.templates.cpp', 'main.cpp').format(project_name=project.name)

    with open('CMakeLists.txt', 'w') as file:
        file.write(cmake_root)
    with open('src/main.cpp', 'w') as file:
        file.write(main)

    return project

@router.handler("lib")
def project_lib(args: List[str], old_project: Optional[Project]) -> Project:
    assert_error(len(args) > 0, "Project name not specified")
    assert_error(len(args) == 1, "Too many arguments")
    assert_error(old_project is None, "Project already created")
    init_folders()

    project = Project(name=args[0], type='lib', files=[f'{args[0]}.cpp'])
    cmake_root = read_text('meerkatpm.templates.cmake', 'CMakeLists.txt').format(project_name=project.name)
    lib_cpp = read_text('meerkatpm.templates.cpp', 'file.cpp').format(file_name=project.name)
    lib_h = read_text('meerkatpm.templates.cpp', 'file.h')\
                .format(file_name=project.name,
                        FILE_CAPS=project.name.upper(),
                        author='<Your name here>',
                        author_email='<Your email here>',
                        date=datetime.date.today(),
                        year=datetime.date.today().year)
    
    with open('CMakeLists.txt', 'w') as file:
        file.write(cmake_root)
    with open(f'src/{project.name}.cpp', 'w') as file:
        file.write(lib_cpp)
    with open(f'include/{project.name}.h', 'w') as file:
        file.write(lib_h)
    
    return project
