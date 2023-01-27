from typing import List, Optional, Literal, Dict, Tuple

from meerkatpm.utils import UsageError, progress_report

class Module:
    class Partial:
        def __init__(self, module: 'Module', children: List['Module.Partial'],
                    dependencies: List[str]) -> None:
            self.module = module
            self.children = children
            self.dependencies = dependencies
        
        def resolve(self, modules: Dict[str, 'Module']) -> 'Module':
            for dependency in self.dependencies:
                if dependency not in modules:
                    raise UsageError(
                        f"Cannot resolve dependencies of module '{self.module.name}': unknown module '{dependency}'")
                self.module.dependencies.append(modules[dependency])
            for child in self.children:
                self.module.submodules.append(child.resolve(modules))

            return self.module

    def __init__(self, name: str,
                headers: List[str], sources: List[str],
                submodules: List["Module"]=[], dependencies: List["Module"]=[],):
        self.name = name
        self.submodules = submodules
        self.dependencies = dependencies
        self.headers = headers
        self.sources = sources

    def reorder_submodules(self, order: List['Module']) -> None:
        submodule_set = set(self.submodules)
        self.submodules = [module for module in order if module in submodule_set]
        for submodule in self.submodules:
            submodule.reorder_submodules(order)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'dependencies': [d.name for d in self.dependencies],
            'submodules': [s.to_dict() for s in self.submodules],
            'sources': self.sources,
            'headers': self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        required_keys = {'name', 'dependencies', 'submodules', 'sources', 'headers'}
        if not required_keys.issubset(data.keys()):
            raise UsageError(f"Missing required keys: {required_keys - data.keys()}")
        
        unknown_keys = data.keys() - required_keys
        if unknown_keys:
            raise UsageError(f"Unknown keys: {unknown_keys}")
        
        children = [Module.from_dict(submodule_data) for submodule_data in data['submodules']]
        dependencies: List[str] = data['dependencies']
        return cls.Partial(
                cls(data['name'], sources=data['sources'], headers=data['headers']),
                children, dependencies)

        
class Project:
    def __init__(self, name: str, type: Literal['exe', 'lib'],
                sources: List[str], headers: List[str],
                modules: List[Module] = []):
        self.name = name
        self.type = type
        self.modules = modules
        self.sources = sources
        self.headers = headers

    def get_compilation_order(self) -> List['Module']:
        compiled_modules = []
        to_compile = self.modules.copy()
    
        while to_compile:
            for module in to_compile:
                dependencies_compiled = all(dependency in compiled_modules for dependency in module.dependencies)

                if dependencies_compiled:
                    compiled_modules.append(module)
                    to_compile.remove(module)
                    for submodule in module.submodules:
                        to_compile.append(submodule)
                    break
                else:
                    # Check for dependency cycle
                    cycle = self.detect_cycle(module)
                    if cycle:
                        raise UsageError("Dependency cycle detected: " + cycle)

        return compiled_modules

    def detect_cycle(self, module, path=[], visited=set()) -> Optional[str]:
        """Helper function to detect a dependency cycle using DFS"""
        path.append(module)
        visited.add(module)
        for dependency in module.dependencies:
            if dependency in path:
                cycle = " -> ".join([str(m) for m in path[path.index(dependency):] + [dependency]])
                return cycle
            elif dependency not in visited:
                cycle = self.detect_cycle(dependency, path, visited)
                if cycle:
                    return cycle
        path.pop()
        return None
    
    @progress_report("Reordering modules for compilation")
    def reorder_for_compilation(self) -> None:
        order = self.get_compilation_order()
        module_set = set(self.modules)
        self.modules = [module for module in order if module in module_set]
        for module in self.modules:
            module.reorder_submodules(order)


    def to_dict(self) -> Dict:
        data = {
            "name": self.name,
            "type": self.type,
            "sources": self.sources,
            "headers": self.headers,
            "modules": [module.to_dict() for module in self.modules]
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        required_keys = {'name', 'type', 'modules', 'sources', 'headers'}
        if not required_keys.issubset(data.keys()):
            raise ValueError(f"Missing required keys. Got {data.keys()}, expected {required_keys}")
        unknown_keys = data.keys() - required_keys
        if unknown_keys:
            raise ValueError(f"Unknown keys {unknown_keys}")

        partial_modules = [Module.from_dict(module_data) for module_data in data['modules']]
        name_to_module = {p.module.name: p.module for p in partial_modules}
        modules = [partial.resolve(name_to_module) for partial in partial_modules]

        return cls(data['name'], data['type'], data['sources'], data['headers'], modules)

