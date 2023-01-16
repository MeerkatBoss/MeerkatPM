from importlib.resources import read_text
from typing import List

from .router import Router
from meerkatpm.utils import assert_error

router = Router("project")

@router.handler("new")
def project_new(args: List[str]) -> None:
    assert_error(len(args) > 0, "Project name not specified")
    assert_error(len(args) == 1, "Too many arguments for 'project new'")
    main: str = read_text('meerkatpm.templates', 'main.cpp')
    print(main.format(project_name=args[0]))
