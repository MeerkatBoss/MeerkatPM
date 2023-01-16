from typing import List, Literal

def cmake_add_subdirectories(dirs: List[str]) -> str:
    return "".join([f"add_subdirectory({dir})\n" for dir in dirs])

def cmake_link_dependencies(
                        name: str,
                        deps: List[str],
                        type: Literal["PUBLIC", "PRIVATE"]) -> str:
    if deps is None or len(deps) == 0:
        return ''
    return f"target_link_libraries({name} {type} {' '.join(deps)})\n"