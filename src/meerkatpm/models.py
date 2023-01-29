from typing import List, Optional, Literal, Dict, Set

from meerkatpm.utils import UsageError, first_or_none

class Module:
    class Partial:
        def __init__(self, module: 'Module', children: List['Module.Partial'],
                    dependencies: List[str]) -> None:
            self.module = module
            self.children = children
            self.dependencies = dependencies
        
        def resolve_dependencies(self, modules: Dict[str, 'Module']) -> 'Module':
            for dependency in self.dependencies:
                if dependency not in modules:
                    raise UsageError(
                        f"Cannot resolve dependencies of module '{self.module.name}': unknown module '{dependency}'")
                self.module.dependencies.append(modules[dependency])
            for child in self.children:
                child.module.full_name = self.module.full_name + '/' + child.module.name
                self.module.submodules.append(child.resolve_dependencies(modules))

            return self.module

    def __init__(self, name: str,
                headers: List[str], sources: List[str],
                submodules: List["Module"]=[], dependencies: List["Module"]=[],):
        self.name = name
        self.full_name = name
        self.submodules = submodules or []
        self.dependencies = dependencies or []
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

    def __str__(self) -> str:
        return self.full_name
    
    def __repr__(self) -> str:
        return f"<Module '{self.full_name}'; deps: {repr(self.dependencies)}; subm: {repr(self.submodules)}>"
    
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
                sources: List[str], headers: List[str], version='0.0.1',
                modules: List[Module] = [], author='',
                author_email='', description=''):
        self.name = name
        self.type = type
        self.version = version
        self.author = author
        self.author_email = author_email
        self.description = description
        self.modules = modules or []
        self.sources = sources
        self.headers = headers
        self.module_dict = self.get_name_dict(modules)
    
    def get_name_dict(self, modules_list: List[Module]) -> Dict[str, Module]:
        modules = modules_list.copy()
        visited: Set[Module] = set()
        name_dict: Dict[str, Module] = {}
        
        while modules:
            current = modules.pop(0)
            if current in visited:
                continue
            if current.name in name_dict:
                raise UsageError(
                    f"Duplicate module name '{current.name}' "
                    f"(modules '{name_dict[current.name].full_name}' and '{current.full_name}')"
                )
            visited.add(current)
            name_dict[current.name] = current
            modules.extend(current.submodules)
        
        return name_dict

    def get_module(self, path: str) -> Optional[Module]:
        parts = path.split('/')
        current = self.modules.copy()
        found = None
        for part in parts:
            found = first_or_none(module for module in current if module.name == part)
            if found is None:
                return None
            current = found.submodules
        return found
    
    def add_module(self, path: str, module: Module):
        if self.get_module(path):
            raise UsageError(f"Module '{path}' already exists")
        module_name = path.rsplit('/', 1)[-1]
        assert module_name == module.name
        if module_name in self.module_dict:
            raise UsageError(
                f"Module with name '{module_name}' already exists "
                f"(module '{self.module_dict[module_name].full_name}')"
            )
        module.full_name = path
        if '/' not in path:
            self.modules.append(module)
        else:
            parent_path = path.rsplit('/', 1)[0]
            parent = self.get_module(parent_path)
            if not parent:
                raise UsageError(f"Parent module '{parent_path}' not found.")
            parent.submodules.append(module)
        self.module_dict[module_name] = module

    def delete_module(self, path: str):
        module = self.get_module(path)
        if not module:
            raise UsageError(f"Module '{path}' not found.")
            
        # Check if module is a dependency of any other module or submodule
        queue = self.modules.copy()
        visited = set()
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if module in current.dependencies:
                raise UsageError(
                    f"Cannot delete module '{module.full_name}', as it is a dependency of '{current.full_name}'.")
            
            queue.extend(current.submodules)
        
        module_name = path.rsplit('/', 1)[-1]
        if '/' in path:
            parent_path = path.rsplit('/', 1)[0]
            parent = self.get_module(parent_path)
            assert parent # never throws, parent exists because child exists
            parent.submodules.remove(module)
        else:
            self.modules.remove(module)
        del self.module_dict[module_name]


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
            "version": self.version,
            "author": self.author,
            "author_email": self.author_email,
            "description": self.description,
            "sources": self.sources,
            "headers": self.headers,
            "modules": [module.to_dict() for module in self.modules]
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        required_keys = {
            'name', 'type', 'version', 'modules', 'sources', 'headers', 'author', 'author_email', 'description'}
        if not required_keys.issubset(data.keys()):
            raise UsageError(f"Missing required keys. Got {data.keys()}, expected {required_keys}")
        unknown_keys = data.keys() - required_keys
        if unknown_keys:
            raise UsageError(f"Unknown keys {unknown_keys}")

        partial_modules = [Module.from_dict(module_data) for module_data in data['modules']]
        name_to_module = {p.module.name: p.module for p in partial_modules}
        modules = [partial.resolve_dependencies(name_to_module) for partial in partial_modules]

        return cls(name=data['name'], type=data['type'], version=data['version'],
                    sources=data['sources'], headers=data['headers'],
                    modules=modules, author=data['author'],
                    author_email=data['author_email'], description=data['description'])

