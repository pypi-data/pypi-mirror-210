from . import messages as _messages

import os as _os
import elevate as _elevate


def require_root(auto_elevate=False):
    if auto_elevate:
        _elevate.elevate(graphical=False)

    if _os.geteuid() != 0:
        _messages.critical_error('Program must be run as root')
