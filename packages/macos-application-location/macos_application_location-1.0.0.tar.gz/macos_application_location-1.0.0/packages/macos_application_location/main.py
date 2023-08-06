import pathlib
import platform
import sys

import psutil


def get() -> pathlib.Path:
    if platform.system() != 'Darwin':
        raise EnvironmentError('This function is only available on macOS')

    if pathlib.Path.cwd() != pathlib.Path.root:
        return pathlib.Path.cwd() / sys.argv[0]

    return pathlib.Path(psutil.Process().cmdline()[0]).parent.parent.parent
