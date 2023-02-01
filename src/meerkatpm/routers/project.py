import os
import shutil

from importlib.resources import read_text, path
from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error, progress_report
from meerkatpm.models import Project
from meerkatpm.codegen import get_cpp_header, get_cpp_source

router = Router("project")

@progress_report("Initializing project structure")
def init_folders() -> None:
    os.mkdir('.vscode')
    os.mkdir('lib')
    os.mkdir('lib/include')
    os.mkdir('include')
    os.mkdir('src')
    os.mkdir('doxygen')
    os.mkdir('build')
    os.mkdir('build/Debug')
    os.mkdir('build/Release')
    os.mkdir('dist')

    with path('meerkatpm.templates', 'Doxyfile') as doxyfile:
        shutil.copy(doxyfile, os.getcwd())
    with path('meerkatpm.templates', 'gitignore') as gitignore:
        shutil.copy(gitignore, os.getcwd()+'/'+'.gitignore')
    with path('meerkatpm.templates', 'settings.json') as settings:
        shutil.copy(settings, os.getcwd()+"/.vscode")
    


@progress_report("Generating cmake files")
def add_cmake(project_name: str) -> None:
    with path('meerkatpm.templates.cmake', 'run.cmake') as run_cmake:
        shutil.copy(run_cmake, os.getcwd())
    with path('meerkatpm.templates.cmake', 'cmake_uninstall.cmake') as uninstall_cmake:
        shutil.copy(uninstall_cmake, os.getcwd())
    cmake_root = read_text('meerkatpm.templates.cmake', 'CMakeLists.txt').format(project_name=project_name)
    with open('CMakeLists.txt', 'w') as file:
        file.write(cmake_root)


def assert_creation_args(args: List[str], old_project: Optional[Project]) -> None:
    assert_error(len(args) > 0, "Project name not specified")
    assert_error(len(args) == 1, "Too many arguments")
    assert_error(old_project is None, "Project already created")
    
    
@router.handler("exe")
def project_exe(args: List[str], old_project: Optional[Project]) -> Project:
    assert_creation_args(args, old_project)

    name = args[0]
    init_folders()
    add_cmake(name)

    project = Project(name=args[0], type='exe', sources=['main.cpp'], headers=[])
    main = read_text('meerkatpm.templates.cpp', 'main.cpp').format(project_name=project.name)

    with open('src/main.cpp', 'w') as file:
        file.write(main)

    print(f"Created project '{project.name}'")
    return project


@router.handler("lib")
def project_lib(args: List[str], old_project: Optional[Project]) -> Project:
    assert_creation_args(args, old_project)

    name = args[0]
    init_folders()
    add_cmake(name)

    project = Project(name=name, type='lib', sources=[f'{args[0]}.cpp'], headers=[f'{args[0]}.h'])
    
    with open(f'src/{project.name}.cpp', 'w') as file:
        file.write(get_cpp_source(project.name))
    with open(f'include/{project.name}.h', 'w') as file:
        file.write(get_cpp_header(project.name, project))
    
    print(f"Created project '{project.name}'")
    return project

@router.handler("import")
def project_import(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found")
    assert project
    assert_error(len(args) > 0, "Imported project archive name not specified")
    assert_error(len(args) < 2, "Too many arguments")

    filename = args[0]

    assert_error(os.path.exists(filename), f"Cannot find file {filename}")
    assert_error(os.path.isfile(filename), f"{filename} is a directory")
    assert_error(filename.endswith('.tar.gz'), "Invalid archive format")

    os.mkdir('imports')
    shutil.unpack_archive(filename, 'imports')
    if os.path.exists('imports/lib'):
        shutil.copytree('imports/lib', 'lib', dirs_exist_ok=True)
    if os.path.exists('imports/include'):
        shutil.copytree('imports/include', 'lib/include', dirs_exist_ok=True)
    shutil.rmtree('imports')
    
    return project
