import os.path
from Globals import package_home

GLOBALS = globals()
PACKAGE_HOME = os.path.dirname(package_home(GLOBALS))

if not PACKAGE_HOME.endswith('tests'):
    PACKAGE_HOME = os.path.join(PACKAGE_HOME, 'tests')
