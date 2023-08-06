import importlib as _importlib
from types import ModuleType as _ModuleType

def reload_module(module: _ModuleType):
    _importlib.reload(module)

