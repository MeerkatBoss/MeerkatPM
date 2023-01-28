import os
import shutil

from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error
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

    name = path.rsplit('/', 1)[-1]
    module = Module(name=name, sources=[f'{name}.cpp'], headers=[f'{name}.h'])
    project.add_module(path, module)

    os.mkdir(f'src/{path}')
    
    with open(f'src/{path}/{module.name}.cpp', 'w') as file:
        file.write(get_cpp_source(module.name))
    with open(f'src/{path}/{module.name}.h', 'w') as file:
        file.write(get_cpp_header(module.name, project))

    return project


@router.handler('rm')
def module_rm(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) <= 1, "Too many arguments")
    path = args[0]
    project.delete_module(path)
    
    shutil.rmtree(f'src/{path}')

    return project


