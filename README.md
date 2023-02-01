# Meerkat Project Manager
MeerkatPM is a simple command-line tool for management of projects in C/C++.

## Installation
For installation info check [here](BUILDING.md)

## Project manifest
MeerkatPM uses `manifest.yaml` to edit and build project. You can edit this manifest manually, or make use of
`mbpm` command tool to do it for you.

`manifest.yaml` is a collection of named fields. The fields are as follows:
- *name* - project name (must be non-empty and only contain letters of latin alphabet)
- *version* - project version (must be non-empty)
- *author* - project author name (may be an empty string)
- *author_email* - project author contact e-mail address (may be an empty string)
- *description* - a brief description of a project (may be an empty string)
- *sources* - list of project source file names (must be non-empty for projects of type `exe`)
- *headers* - list of project header file names (must be non-empty for projects of type `lib`)
- *modules* - list of project modules (may be empty)
    - *name* - module name (must be non-empty and only contain letters of latin alphabet). All module names must be
        unique.
    - *dependencies* - names of modules this module depends on (may be empty). Dependency must either be a top-level
        module (i.e. element of *modules* field in project) or be nested in the same module as current module.
    - *submodules* - list of nested modules
    - *sources* - list of module source files (may be empty)
    - *headers* - list of module header files (may be empty)


## Usage
The basic syntax for using MeerkatPM is following:
```bash
mbpm <command-scope> <command> [arguments]
```
### `project` scope
- `mbpm project exe <name>` - Initialize new project with given name of type 'executable' in current directory.
- `mbpm project lib <name>` - Initialize new project with given name of type 'library' in current directory.
- `mbpm project import <path-to-archive>` - Import package, previously built by `mbpm build package`

### `module` scope
- `mbpm module add <name>` - Add new module with given name to project. Nested modules are identified by their
    '/'-separated path. For example, the following commands creates a submodule of `module1` named `module2`:
    ```bash
    $ mbpm module add module1/module2
    ```
- `mbpm module rm <name>` - Delete module, identified by path as in `module add`, from the project. Deleted module
    must not be a dependency of any other module
- `mbpm module depend <target> <dependency>` - Add dependency of one module on another. `dependency` must either be
    a top-level module (i.e. module with no parent module), or be nested in the same submodule as `target`. Modules
    are identified by their path as in previous commands.
- `mbpm module nodepend <target> <dependency>` - Remove dependency of one module or another. Modules are identified by
    their path as in previous commands.

### `file` scope
- `mbpm file add <name>` - Add new file to project. If prefixed with module path, e.g. `module1/module1/file.cpp` or
    `module0/file.h`, file would be added to the corresponding module instead. Only permitted file types are `.c`,
    `.cpp`, `.h`, `.hpp`. When adding `.c` or `.cpp` file, the `.h` file with the same name (without file extension)
    would be added as well.
- `mbpm file rm <name>` - Delete file from project. Files are identified by path as in `file add` command.

### `build` scope
- `mbpm build debug`, `mbpm build release` - Build project in given configuration
- `mbpm build clean` - Clean all build info
- `mbpm build package` - Create a package, that can be later imported by `project import` command. Before building
    package, project must be built in `release` configuration.

### `run` scope
All command from this scope are only applicable to project of type 'executable'
- `mbpm run debug [arg-list]`, `mbpm run release [arg-list]` - Run project in given configuration, passing any
    additional arguments to it.
- `mbpm run gdb` - **Requires gdb installed** Start debugging session of `debug` configuration in `gdb`
