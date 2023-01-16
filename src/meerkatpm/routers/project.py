from importlib.resources import read_text
from typing import List, Optional

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error
from meerkatpm.models import Project

router = Router("project")

@router.handler("exe")
def project_exe(args: List[str], project: Optional[Project]) -> Project:
    raise NotImplementedError
    assert_error(len(args) > 0, "Project name not specified")
    assert_error(len(args) == 1, "Too many arguments")
    assert_error(project is None, "Project already created")

    main: str = read_text('meerkatpm.templates.cpp', 'main.cpp')
    print(main.format(project_name=args[0]))
