import pathlib
import platform
import sys


def get() -> pathlib.Path:
    if platform.system() != 'Darwin':
        raise EnvironmentError('This function is only available on macOS')

    p: pathlib.Path = pathlib.Path.cwd() / sys.argv[0]

    if '.app/Contents/MacOS/' in p:
        p = p.parent.parent.parent

    return p
