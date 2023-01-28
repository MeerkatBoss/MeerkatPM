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

@router.handler('depend')
def module_depend(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) > 1, "No dependency specified")
    assert_error(len(args) <= 2, "Too many arguments")
    target_path, dependency_path = args
    target = project.get_module(target_path)
    dependency = project.get_module(dependency_path)
    assert_error(target is not None, f"Cannot find module '{target_path}'")
    assert_error(dependency is not None, f"Cannot find module '{dependency_path}'")
    assert target and dependency # never throws
    assert_error(dependency not in target.dependencies, f"'{target_path}' already depends on '{dependency_path}'")

    if '/' in dependency_path:
        parent = dependency_path.rsplit('/', 1)[0]
        assert_error(
            parent == target_path.rsplit('/', 1)[0],
            f"Failed to add dependency. Submodules '{target_path}' and '{dependency_path}' do not share a parent.")

    target.dependencies.append(dependency)

    return project

@router.handler('nodepend')
def module_nodepend(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) > 1, "No dependency specified")
    assert_error(len(args) <= 2, "Too many arguments")
    target_path, dependency_path = args
    target = project.get_module(target_path)
    dependency = project.get_module(dependency_path)
    assert_error(target is not None, f"Cannot find module '{target_path}'")
    assert_error(dependency is not None, f"Cannot find module '{dependency_path}'")
    assert target and dependency # never throws
    assert_error(dependency in target.dependencies, f"Module '{target_path}' does not depend on '{dependency_path}'")

    target.dependencies.remove(dependency)

    return project
