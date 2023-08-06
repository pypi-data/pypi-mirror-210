import platform as _platform
import subprocess as _subprocess
from shlex import split as _split
from subprocess import CalledProcessError


# runs a command, depeding on the current OS
#   returns True if the program exits with return code zero, False otherwise
def execute(command: str) -> bool:
    exit_status = _subprocess.check_call(_split(command))
    return exit_status == 0

# runs a command, depeding on the current OS
#   the output is returned in the specified type (default: bytes)
#   if a command returns a non-zero exit code the program raises an exception (default behavior) or returns a given value (by default: None)
def get_output(command: str, return_type = bytes, on_error = None):
    try:
        return return_type(_subprocess.check_output(_split(command)))
    except CalledProcessError as e:
        if on_error is None:
            raise e
        return return_type(on_error())
    