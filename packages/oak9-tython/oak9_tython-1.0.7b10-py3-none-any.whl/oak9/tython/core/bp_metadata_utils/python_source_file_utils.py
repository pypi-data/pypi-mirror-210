import ast
import importlib.util
import inspect
from pathlib import Path
from typing import List
from contextlib import contextmanager
import os
from core.types import Blueprint

# No use-cases for Class-level docstrings yet.
NODE_TYPES = {
    ast.ClassDef: 'Class',
    ast.FunctionDef: 'Function/Method',
    ast.Module: 'Module'
}


def get_docstrings(source):
    """Parse Python source code and yield a tuple of ast node instance, name,
    line number and docstring for each function/method, class and module.

    The line number refers to the first line of the docstring. If there is
    no docstring, it gives the first line of the class, function or method
    block, and docstring is None.
    """
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, tuple(NODE_TYPES)):
            docstring = ast.get_docstring(node)
            lineno = getattr(node, 'lineno', None)

            if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Str)):
                # lineno attribute of docstring node is where string ends
                lineno = node.body[0].lineno - len(node.body[0].value.s.splitlines()) + 1

            yield node, getattr(node, 'name', None), lineno, docstring


def is_customer_blueprint(path: str) -> bool:
    with open(path) as fd:
        source = fd.read()

    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            if 'Blueprint' in [n.id for n in node.bases]:
                fd.close()
                return True

    fd.close()
    return False


def module_from_file(module_name, file_path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ModuleNotFoundError as e:
        print("Raised Exception: " + str(e))
        return None

    return module


def get_blueprint_classes(path_to_py_file) -> List:
    file_name = Path(path_to_py_file).name
    module = module_from_file(file_name.removesuffix('.py'), path_to_py_file)

    if not module:
        raise ModuleNotFoundError

    class_members = inspect.getmembers(module, inspect.isclass)
    blueprint_classes = []

    '''
        check if blueprint class exists
        '''
    for cls in class_members:
        if is_blueprint_class(cls):
            blueprint_classes.append(cls)

    return blueprint_classes


def is_blueprint_class(cls) -> bool:
    try:
        inspect.getattr_static(cls[1], 'blueprint_type')
        if cls[1].__name__ != 'Blueprint':
            return True
        return False
    except AttributeError:
        return False


from contextlib import contextmanager


@contextmanager
def add_to_path(p):
    import sys
    old_path = sys.path
    old_modules = sys.modules
    sys.modules = old_modules.copy()
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path
        sys.modules = old_modules


def path_import(absolute_path):
    """implementation taken from https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly"""
    with add_to_path(os.path.dirname(absolute_path)):
        spec = importlib.util.spec_from_file_location(absolute_path, absolute_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
