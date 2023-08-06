import sys
import os
import inspect

os.environ['GRAVITAS_ROOT'] = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, os.environ['GRAVITAS_ROOT'])
os.environ['GRAVITAS_SO'] = os.path.join(os.environ['GRAVITAS_ROOT'], 'grav.so')

if not os.path.exists(os.environ['GRAVITAS_SO']):
    os.system('cd $GRAVITAS_ROOT && gcc gravlib.c -shared -o grav.so')

from .lib import *
