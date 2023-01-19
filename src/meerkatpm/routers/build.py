import subprocess

from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.models import Project
from meerkatpm.utils import assert_error

router = Router("build")

@router.handler('debug')
def build_debug(args: List[str], project: Optional[Project]) -> Project:
    assert_error(args == [], "Too many arguments")
    assert_error(project is not None, "No project manifest found")
    assert project is not None

    subprocess.run(['cmake', '--build', 'build/Debug'])

    return project


@router.handler('release')
def build_release(args: List[str], project: Optional[Project]) -> Project:
    assert_error(args == [], "Too many arguments")
    assert_error(project is not None, "No project manifest found")
    assert project is not None

    subprocess.run(['cmake', '--build', 'build/Release'])

    return project


@router.handler('clean')
def build_clean(args: List[str], project: Optional[Project]) -> Project:
    assert_error(args == [], "Too many arguments")
    assert_error(project is not None, "No project manifest found")
    assert project is not None

    subprocess.run(['cmake', '--build', 'build/Debug', '--target', 'clean'])
    subprocess.run(['cmake', '--build', 'build/Release', '--target', 'clean'])

    return project
