from meerkatpm.models import Module, Project

from .helpers import cmake_add_subdirectories, cmake_link_dependencies

def get_module_cmake(module: Module) -> str:
    result = f"add_library({module.name} {' '.join(module.files)})\n"
    submodules = [m.name for m in module.submodules]

    result += cmake_add_subdirectories(submodules)
    result += cmake_link_dependencies(module.name, module.dependencies + submodules, "PUBLIC")

    result += f"target_include_directories({module.name} PUBLIC ${{CMAKE_CURRENT_LIST_DIR}})\n"
    return result

def get_project_cmake(project: Project) -> str:
    type = 'executable' if project.type == 'exe' else 'library'
    result = f"add_{type}({project.name} {' '.join(project.files)})\n"

    modules = [m.name for m in project.modules]
    
    result += cmake_add_subdirectories(modules)
    result += cmake_link_dependencies(project.name, modules, "PRIVATE")

    include_dir = '${PROJECT_SOURCE_DIR}/include/' 
    result += f'target_include_directories({project.name} PUBLIC {include_dir})\n'

    if project.type == 'exe':
        result += f"add_run_target({project.name})\n"

    result += f"install(TARGETS {project.name} RUNTIME CONFIGURATIONS Release)\n"

    if project.type == 'lib':
        headers = (file.replace('.c', '.h') for file in project.files)
        headers = (include_dir + file for file in headers)
        headers = ' '.join(headers)
        result += f"install(FILES {headers} TYPE INCLUDE)\n"


    return result
