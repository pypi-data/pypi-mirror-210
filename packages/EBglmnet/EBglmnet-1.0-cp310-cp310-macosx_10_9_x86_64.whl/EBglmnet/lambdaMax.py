import numpy as np
import ctypes
from loadEBglmnetLib import loadEBglmnetLib

def lambdaMax(BASIS, Target, Epis=False):
    episInt = int(Epis);

    X = np.asfortranarray(BASIS);
    X = X.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    Y = np.asfortranarray(Target);
    Y = Y.ctypes.data_as(ctypes.POINTER(ctypes.c_double));
    n, k = BASIS.shape
    N = np.asarray(n);
    N = N.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    K = np.asarray(k);
    K = K.ctypes.data_as(ctypes.POINTER(ctypes.c_int));

    episInt = np.asarray(episInt);
    episInt= episInt.ctypes.data_as(ctypes.POINTER(ctypes.c_int));
    lmax = np.zeros(1)
    lmax = np.asfortranarray(lmax);
    lmax = lmax.ctypes.data_as(ctypes.POINTER(ctypes.c_double));

    EBglmnetLib = loadEBglmnetLib()

    EBglmnetLib.ProjectCorr(N, K, Y,X,lmax, episInt);
    result = np.ctypeslib.as_array(lmax, shape=(1, 1));
    return result[0][0];