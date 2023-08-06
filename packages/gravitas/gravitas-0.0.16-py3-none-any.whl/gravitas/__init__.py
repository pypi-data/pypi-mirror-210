import sys
import os
import inspect

os.environ['GRAVITAS_ROOT'] = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, os.environ['GRAVITAS_ROOT'])
os.environ['GRAVITAS_SO'] = os.path.join(os.environ['GRAVITAS_ROOT'], 'grav.so')

if os.path.exists(os.environ['GRAVITAS_SO']):
    os.remove(os.environ['GRAVITAS_SO'])
if not os.path.exists(os.environ['GRAVITAS_SO']):
    print("Building .so!")
    os.system('cd $GRAVITAS_ROOT && gcc gravlib.c -shared -o grav.so')

os.environ['GRAVITAS_ROOT_CP'] = os.environ['GRAVITAS_ROOT']

from .lib import *
