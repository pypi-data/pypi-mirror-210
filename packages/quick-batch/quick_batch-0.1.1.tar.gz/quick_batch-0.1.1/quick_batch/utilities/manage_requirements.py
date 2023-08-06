import ast
import sys
from utilities import log_exceptions


def get_processor_requirements(processor):
    # Parse the processor.py file to get the imported module names
    with open(processor, 'r') as file:
        tree = ast.parse(file.read())

    imported_modules = set()

    # Traverse the abstract syntax tree to extract import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module)

    # Exclude built-in and standard libraries
    built_in_modules = set(sys.builtin_module_names)
    standard_modules = set(sys.modules.keys())
    excluded_modules = built_in_modules.union(standard_modules)

    # Get the required external modules
    installed_modules = sorted(imported_modules.difference(excluded_modules))

    return installed_modules


def write_requirements(required_modules, file_path):
    with open(file_path, 'w') as file:
        for module in required_modules:
            file.write(module + '\n')


@log_exceptions
def make_requirements(processor, container_path):
    # get requirements for processor.py
    installed_modules = get_processor_requirements(processor)

    # write requirements to file
    write_requirements(installed_modules, container_path)
