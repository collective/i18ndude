import os
import sys
from contextlib import contextmanager


def package_home(globals_dict):
    __name__ = globals_dict['__name__']
    m = sys.modules[__name__]
    if hasattr(m, '__path__'):
        r = m.__path__[0]
    elif "." in __name__:
        r = sys.modules[__name__[:__name__.rfind('.')]].__path__[0]
    else:
        r = __name__
    return os.path.abspath(r)

GLOBALS = globals()
PACKAGE_HOME = os.path.dirname(package_home(GLOBALS))

if not PACKAGE_HOME.endswith('tests'):
    PACKAGE_HOME = os.path.join(PACKAGE_HOME, 'tests')


@contextmanager
def suppress_stdout():
    # Taken with thanks from Dave Smith's site:
    # http://thesmithfam.org/blog/2012/10/25/
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
