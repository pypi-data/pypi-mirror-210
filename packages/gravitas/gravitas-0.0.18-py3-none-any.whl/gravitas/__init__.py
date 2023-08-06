import sys
import os
import inspect

_ARTIFACTS = []
_MODELNAMES = ['EGM96', 'GRGM360', 'MRO120F']

# COMPILER SETUP
if sys.platform == "linux" or sys.platform == "linux2":
    try:
        os.system('module load gcc') 
        # If we're on a compute cluster, intel compilers might be loaded
    except:
        print("Module load errored, compilation may fail")
        pass


os.environ['GRAVITAS_ROOT'] = os.path.dirname(
    os.path.abspath(inspect.getsourcefile(lambda: 0))
)
sys.path.insert(0, os.environ['GRAVITAS_ROOT'])
os.environ['GRAVITAS_SO'] = os.path.join(os.environ['GRAVITAS_ROOT'], 'grav.so')
_ARTIFACTS.append(os.path.join(os.environ['GRAVITAS_ROOT'], 'grav.o'))

if os.path.exists(os.environ['GRAVITAS_SO']) and 'GRAVITAS_FORCE_COMPILE' in os.environ:
    os.remove(os.environ['GRAVITAS_SO'])

if not os.path.exists(os.environ['GRAVITAS_SO']):
    cargs = '-fPIC -Wall -O3 -std=c99'
    nwithext = lambda ext: " ".join([n+f".{ext}" for n in _MODELNAMES])
    all_to_obj = [f'gcc -c {cargs} {n}.c -o {n}.o' for n in _MODELNAMES]
    _ARTIFACTS.extend([os.path.join(os.environ['GRAVITAS_ROOT'], f'{x}.o') for x in _MODELNAMES])
    cmds = [f'gcc -c {cargs} gravlib.c -o grav.o',
            *all_to_obj,
            f'gcc grav.o {nwithext("o")} -shared -Wall -o grav.so']
    os.chdir(os.environ['GRAVITAS_ROOT'])
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
    for art in _ARTIFACTS:
        os.remove(art)

from .lib import *