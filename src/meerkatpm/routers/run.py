import os

from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.models import Project
from meerkatpm.utils import assert_error

router = Router("run")

@router.handler("debug")
def run_debug(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found")
    assert project is not None # never throws
    assert_error(project.type == 'exe', "Cannot run project of type 'lib'") # TODO: add running examples

    run_args = []
    if args != []:
        txt_args = ' '.join(args)
        run_args = ['--', f'ARGS={txt_args}']

    os.execlp('cmake', 'cmake', '--build', 'build/Debug', '--target', f'run_{project.name}', *run_args)


@router.handler("release")
def run_release(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found")
    assert project is not None # never throws
    assert_error(project.type == 'exe', "Cannot run project of type 'lib'") # TODO: add running examples

    run_args = []
    if args != []:
        txt_args = ' '.join(args)
        run_args = ['--', f'ARGS={txt_args}']

    os.execlp('cmake', 'cmake', '--build', 'build/Release', '--target', f'run_{project.name}', *run_args)


@router.handler("gdb")
def run_gdb(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found")
    assert project is not None # never throws
    assert_error(project.type == 'exe', "Cannot debug project of type 'lib'") # TODO: add running examples
    assert_error(args == [], "When debugging, parameters need to be passed manually.")

    exec_path = f'build/Debug/src/{project.name}'
    assert_error(os.path.exists(exec_path), "Project not built for debug")
    os.execlp('gdb', 'gdb', exec_path)
