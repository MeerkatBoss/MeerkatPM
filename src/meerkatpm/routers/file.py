import os

from typing import List, Optional, Union

from meerkatpm.routers import Router
from meerkatpm.utils import assert_error
from meerkatpm.models import Project, Module
from meerkatpm.codegen import get_cpp_header, get_cpp_source

router = Router('file')

def add_header(path: str, project: Project):
    filename = path.rsplit('/', 1)[-1]
    name = filename.rsplit('.', 1)[0]
    if '/' in path:
        module_path = path.rsplit('/', 1)[0]
        module = project.get_module(module_path)
        assert_error(module is not None, f"Cannot find module '{module_path}'")
        assert module
        assert_error(filename not in module.headers, f"Header '{filename}' already exists in module '{module_path}'")
        module.headers.append(filename)
        with open("src/"+module_path+"/"+filename, 'w') as header:
            header.write(get_cpp_header(name, project))

    else:
        assert_error(filename not in project.headers, f"Header '{filename}' already exists in project")
        project.headers.append(filename)
        with open("include/"+filename, 'w') as header:
            header.write(get_cpp_header(name, project))

def add_source(path: str, project: Project):
    source = path.rsplit('/', 1)[-1]
    name = source.rsplit('.', 1)[0]
    header = name + '.h'
    if '/' in path:
        module_path = path.rsplit('/', 1)[0]
        module = project.get_module(module_path)
        assert_error(module is not None, f"Cannot find module '{module_path}'")
        assert module
        assert_error(source not in module.sources, f"Source file '{source}' already exists in module '{module_path}'")
        if header not in module.headers:
            module.headers.append(header)
            with open("src/"+module_path+"/"+header, 'w') as header_file:
                header_file.write(get_cpp_header(name, project))
        module.sources.append(source)
        with open("src/"+module_path+"/"+source, 'w') as source_file:
            source_file.write(get_cpp_source(name))
    else:
        assert_error(source not in project.sources, f"Source '{source}' already exists in project")
        if header not in project.headers:
            project.headers.append(header)
            with open("include/"+header, 'w') as header_file:
                header_file.write(get_cpp_header(name, project))
        project.sources.append(source)
        with open("src/"+source, 'w') as source_file:
            source_file.write(get_cpp_source(name))

@router.handler('add')
def file_add(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) <= 1, "Too many arguments")
    path = args[0]

    filename = path.rsplit('/', 1)[-1]
    assert_error(
        filename.endswith('.h') or filename.endswith('.hpp') or
        filename.endswith('.c') or filename.endswith('.cpp'),
        "Unsupported file type")
    if filename.endswith('.h') or filename.endswith('.hpp'):
        add_header(path, project)
    else:
        add_source(path, project)

    return project

@router.handler('rm')
def file_rm(args: List[str], project: Optional[Project]) -> Project:
    assert_error(project is not None, "No project manifest found.")
    assert project is not None # never throws
    assert_error(len(args) > 0, "No module name provided")
    assert_error(len(args) <= 1, "Too many arguments")
    path = args[0]

    parent: Union[Project, Module] = project
    filename = path.rsplit('/', 1)[-1]
    filepath = ""
    if '/' in path:
        module = project.get_module(path.rsplit('/', 1)[0])
        assert_error(module is not None, "Module not found")
        assert module
        parent = module
        filepath = path
    elif filename.endswith('.h') or filename.endswith('.hpp'):
        filepath = 'include/'+filename
    else:
        filepath = 'src/'+filename
    
    assert_error(os.path.exists(filepath), f"Failed to locate file '{filepath}'")
    os.remove(filepath)

    if filename.endswith('.h') or filename.endswith('.hpp'):
        parent.headers.remove(filename)
    else:
        parent.sources.remove(filename)

    return project