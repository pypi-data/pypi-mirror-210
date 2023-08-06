from ctypes import *
import numpy as np
import os

lib = CDLL(os.environ['GRAVITAS_SO'])
_GRAV_FUN = lib.egm96_gravity
_SUPPORTED_MODELS = {'EGM96': 360, 'GRGM360': 360, "MRO120F": 120}
_MAX_PTS = int(1e5)

def acceleration(position_ecef: np.ndarray, max_order: int, use_model: str = "EGM96") -> np.ndarray:
    if use_model not in _SUPPORTED_MODELS:
        raise NotImplementedError(f"Model {use_model} is not supported, it must be in: {_SUPPORTED_MODELS}")
    if _SUPPORTED_MODELS[use_model] < max_order:
        raise ValueError(f"The {use_model} model has coefficients to a maximum order of {_SUPPORTED_MODELS[use_model]}, {max_order} input")
    if position_ecef.shape[0] > _MAX_PTS:
        raise ValueError(f"Currently, gravitas is limited to 1e5 points per acceleration() call ({position_ecef.shape[0]} provided)")
    xl, yl, zl = position_ecef[:,0].tolist(), position_ecef[:,1].tolist(), position_ecef[:,2].tolist()
    n = len(xl)
    _GRAV_FUN.argtypes = [POINTER(c_double * n), 
                        POINTER(c_double * n), 
                        POINTER(c_double * n), 
                        c_int,
                        c_int,
                        c_char_p]
    _GRAV_FUN.restype = POINTER(c_double * 3*n)
    x, y, z = (c_double * n)(*xl), (c_double * n)(*yl), (c_double * n)(*zl)
    res = np.array(_GRAV_FUN(x, y, z, n, max_order, use_model.encode('utf-8')).contents[:]).reshape((-1,3))
    os.environ['GRAVITAS_ROOT_CP'] = os.environ['GRAVITAS_ROOT']
    return res

