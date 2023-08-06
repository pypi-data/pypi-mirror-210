from . import messages as _messages

import os as _os

def require_root():
    if _os.geteuid() != 0:
        _messages.critical_error('Program must be run as root')
