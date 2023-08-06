import sys
import os
import inspect

_MODELNAMES = ['EGM96', 'GRGM360', 'MRO120F']

os.environ['GRAVITAS_ROOT'] = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, os.environ['GRAVITAS_ROOT'])
os.environ['GRAVITAS_SO'] = os.path.join(os.environ['GRAVITAS_ROOT'], 'grav.so')

if os.path.exists(os.environ['GRAVITAS_SO']):
    os.remove(os.environ['GRAVITAS_SO'])
if not os.path.exists(os.environ['GRAVITAS_SO']):
    cargs = '-fPIC -Wall -O3'
    nwithext = lambda ext: " ".join([n+f".{ext}" for n in _MODELNAMES])
    all_to_obj = [f'gcc -c {cargs} {n}.c -o {n}.o' for n in _MODELNAMES]
    cmds = [f'gcc -c {cargs} gravlib.c -o grav.o',
            *all_to_obj,
            f'gcc grav.o {nwithext("o")} -shared -Wall -o grav.so']
    os.chdir(os.environ['GRAVITAS_ROOT'])
    for cmd in cmds:
        print(cmd)
        os.system(cmd)

from .lib import *
