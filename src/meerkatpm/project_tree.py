from typing import Optional, List, Dict

from meerkatpm.models import Module, Project
from meerkatpm.utils import assert_error, first_or_none, progress_report

class ProjectTree(Project):
    class Node(Module):
        def __init__(self, module: Module) -> None:
            super().__init__(**module.__dict__)
            self.links: List['ProjectTree.Node'] = []
            self.children: List['ProjectTree.Node'] = []
            pass

        def link_dependencies(self, tree: 'ProjectTree', prefix_="") -> None:
            assert_error(self.name not in tree.module_names.keys(),
                f"Name conflict between modules '{tree.module_names[self.name]}' and '{prefix_+self.name}'")
            tree.module_names[self.name] = prefix_+self.name

            for dependency in self.dependencies:
                resolved = tree.find_module(dependency)
                assert_error(resolved is not None,
                    f"Could not resolve dependencies of {prefix_+self.name}. Unknown module '{dependency}'.")
                assert resolved is not None # never throws
                self.links.append(resolved)
            
            self.children = [ProjectTree.Node(submodule) for submodule in self.submodules]
            for child in self.children:
                child.link_dependencies(tree, prefix_+self.name+'/')
        
        def update_module(self) -> 'Module':
            self.dependencies = [node.name for node in self.links]
            self.submodules: List[Module] = [node.update_module() for node in self.children]
            return self
        

    def __init__(self, project: Project) -> None:
        super().__init__(**project.__dict__)
        self.root = ProjectTree.Node(Module(
            name=self.name,
            description=self.description,
            sources=self.sources,
            submodules=self.modules
        ))
        self.nodes = [ProjectTree.Node(module) for module in project.modules]
        self.module_names: Dict[str, str] = {}
        self.root.link_dependencies(self)
        pass

    def find_module(self, name: str) -> Optional['ProjectTree.Node']:
        return first_or_none(node for node in self.nodes if node.name == name)

    @progress_report("Updating project tree...")
    def update_project(self) -> Project:
        self.root.update_module()
        self.modules = self.root.submodules
        return self
