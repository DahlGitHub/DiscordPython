import pkgutil
import importlib

def walk_packages(path, prefix):
    for module_info in pkgutil.iter_modules(path, prefix):
        if not module_info.ispkg:
            yield module_info.name
        else:
            # Still walk into subpackages to find .py files
            sub_module = importlib.import_module(module_info.name)
            yield from walk_packages(sub_module.__path__, module_info.name + '.')

EXTENSIONS = list(walk_packages(__path__, 'cogs.'))
