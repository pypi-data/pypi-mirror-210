import platform as _platform
from . import commands as _commands


class _Style:
    NORMAL              = b''
    BOLD                = b''
    DIM                 = b''
    ITALIC              = b''
    UNDERLINE           = b''
    UNDERLINE_DOUBLE    = b''
    UNDERLINE_CURLY     = b''
    BLINK               = b''
    REVERSE             = b''
    INVISIBLE           = b''   # Invisible but copy-pasteable
    STRIKETHROUGH       = b''
    OVERLINE            = b''

class _Color:
    WHITE               = b''
    DARKGRAY            = b''
    RED                 = b''
    GREEN               = b''
    YELLOW              = b''
    BLUE                = b''
    PURPLE              = b''
    CYAN                = b''
    LIGHTGRAY           = b''

class _Background:
    NONE                = b''
    DARKGRAY            = b''
    RED                 = b''
    GREEN               = b''
    YELLOW              = b''
    BLUE                = b''
    PURPLE              = b''
    CYAN                = b''
    LIGHTGRAY           = b''

class _TextFormat:
    class Style(_Style):
        pass
    class Color(_Color):
        pass
    class Background(_Background):
        pass
    RESET = b''
    def get_term_len():
        return 0

class _TextFormatLinux:
    class Style(_Style):
        NORMAL              = b'\x1b[0m'
        BOLD                = b'\x1b[1m'
        DIM                 = b'\x1b[2m'
        ITALIC              = b'\x1b[3m'
        UNDERLINE           = b'\x1b[4m'
        UNDERLINE_DOUBLE    = b'\x1b[4:2m'
        UNDERLINE_CURLY     = b'\x1b[4:3m'
        BLINK               = b'\x1b[5m'
        REVERSE             = b'\x1b[7m'
        INVISIBLE           = b'\x1b[8m'
        STRIKETHROUGH       = b'\x1b[9m'
        OVERLINE            = b'\x1b[53m'
    class Color(_Color):
        DARKGRAY            = b'\x1b[30m'
        RED                 = b'\x1b[31m'
        GREEN               = b'\x1b[32m'
        YELLOW              = b'\x1b[33m'
        BLUE                = b'\x1b[34m'
        PURPLE              = b'\x1b[35m'
        CYAN                = b'\x1b[36m'
        LIGHTGRAY           = b'\x1b[37m'
    class Background(_Background):
        DARKGRAY            = b'\x1b[40m'
        RED                 = b'\x1b[41m'
        GREEN               = b'\x1b[42m'
        YELLOW              = b'\x1b[43m'
        BLUE                = b'\x1b[44m'
        PURPLE              = b'\x1b[45m'
        CYAN                = b'\x1b[46m'
        LIGHTGRAY           = b'\x1b[47m'
    RESET                   = b'\x1b[0m'
    def get_term_len():
        return _commands.get_output('tput cols', int, on_error=lambda: 0)

class _TextFormatWindows:
    class Style(_Style):
        pass
    class Color(_Color):
        pass
    class Background(_Background):
        pass
    RESET = b''

    def get_term_len():
        return 0


if _platform.system() == 'Linux':
    TextFormat = _TextFormatLinux
elif _platform.system() == 'Windows':
    TextFormat = _TextFormatWindows
else:
    TextFormat = _TextFormat
