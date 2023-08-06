from . import messages as _messages

import os as _os

def require_root(auto_elevate=True):
    if auto_elevate:
        import elevate as _elevate
        _elevate.elevate(graphical=False)

    if _os.geteuid() != 0:
        _messages.critical_error('Program must be run as root')

def require_os(*os: str):
    import platform as _platform

    if _platform.system() not in os:
        _messages.critical_error('OS not supported')