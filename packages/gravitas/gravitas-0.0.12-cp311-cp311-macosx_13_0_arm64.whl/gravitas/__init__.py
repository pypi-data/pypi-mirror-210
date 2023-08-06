import sys
import os
import inspect

os.environ['GRAVITAS_ROOT'] = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, os.environ['GRAVITAS_ROOT'])

# os.system('gcc gravlib.c -shared -o grav.so')

from .lib import *
