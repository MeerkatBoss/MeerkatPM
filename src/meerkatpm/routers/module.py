import os

from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error, progress_report
from meerkatpm.models import Project, Module
from meerkatpm.codegen import get_cpp_header, get_cpp_source

router = Router('module')

@router.handler('add')
def module_add(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) <= 1, "Too many arguments")
    path = args[0]
    assert_error(project.find_module(path) is None, f"Module '{path}' already exists.")

    path, _, name = path.rpartition('/')
    module = Module(name=name, sources=[f'{name}.cpp'])
    if path:
        parent = project.find_module(path)
        assert_error(parent is not None, f"No module '{path}'.")
        assert parent is not None # never throws
        parent.submodules.append(module)
    else:
        project.modules.append(module)

    os.mkdir(f'src/{module.name}')
    
    with open(f'src/{module.name}/{module.name}.cpp', 'w') as file:
        file.write(get_cpp_source(module.name))
    with open(f'src/{module.name}/{module.name}.hpp', 'w') as file:
        file.write(get_cpp_header(module.name, project))

    return project


# @router.handler('rm')
# def module_rm(args: List[str], project: Optional[Project]) -> Project:
#     assert_error(project is not None, "No project manifest found.")
#     assert project is not None # never throws
#     assert_error(len(args) > 0, "No module name provided")
#     assert_error(len(args) <= 1, "Too many arguments")
#     path = args[0]
#     module = project.find_module(path)

#     return project


