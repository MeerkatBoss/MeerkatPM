import datetime

from itertools import chain
from importlib.resources import read_text, path

from meerkatpm.models import Module, Project

from .helpers import cmake_add_subdirectories, cmake_link_dependencies

def get_module_cmake(module: Module) -> str:
    result = f"add_library({module.name} {' '.join(module.sources)})\n"
    submodules = [m.name for m in module.submodules]
    dependencies = [m.name for m in module.dependencies]

    result += cmake_add_subdirectories(submodules)
    result += cmake_link_dependencies(module.name, dependencies + submodules, "PUBLIC")

    result += f"target_include_directories({module.name} PUBLIC ${{CMAKE_CURRENT_LIST_DIR}})\n"
    return result


def get_project_cmake(project: Project) -> str:
    type = 'executable' if project.type == 'exe' else 'library'
    result = f"add_{type}({project.name} {' '.join(project.sources)})\n"

    modules = [m.name for m in project.modules]
    
    result += cmake_add_subdirectories(modules)
    result += cmake_link_dependencies(project.name, modules, "PRIVATE")

    include_dir = '${PROJECT_SOURCE_DIR}/include/' 

    if project.type == 'exe':
        result += f"add_run_target({project.name})\n"

    result += f"install(TARGETS {project.name} RUNTIME CONFIGURATIONS Release)\n"

    if project.type == 'lib':
        headers = ' '.join(include_dir + file for file in project.headers)
        result += f"install(FILES {headers} TYPE INCLUDE)\n"

    return result


def get_cpp_source(name: str) -> str:
    return read_text('meerkatpm.templates.cpp', 'file.cpp').format(file_name=name)


def get_cpp_header(name: str, project: Project) -> str:
    return read_text('meerkatpm.templates.cpp', 'file.hpp')\
                .format(file_name=name,
                        FILE_CAPS=name.upper(),
                        author='<Your name here>',
                        author_email='<Your email here>',
                        date=datetime.date.today(),
                        year=datetime.date.today().year)
