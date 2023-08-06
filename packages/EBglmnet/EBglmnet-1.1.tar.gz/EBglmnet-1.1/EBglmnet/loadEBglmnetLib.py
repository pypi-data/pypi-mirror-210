"""
defloadEBglmnetLib():
=======================
INPUT ARGUMENTS:
                NONE
=======================
OUTPUT ARGUMENTS:
EBglmnetLib          Returns an EBglmnetLib object with methods that are equivalent
                to the C functions in /src
=======================
"""
import ctypes
import os
EBglmnet_so = 'EBglmnet.cpython-310-darwin.so'

EBglmnet_so = os.path.dirname(__file__) + '/EBglmnet.cpython-310-darwin.so'
EBglmnet_dll = os.path.dirname(__file__) + '/EBglmnet.cpython-310-darwin.dll'

def loadEBglmnetLib():
    if os.name == 'posix':
        EBglmnetLib = ctypes.cdll.LoadLibrary(EBglmnet_so)
        return(EBglmnetLib)
    elif os.name == 'nt':
        # this does not currently work
        raise ValueError('loadEBglmnetLib does not currently work for windows')
        # EBglmnetLib = ctypes.windll.LoadLibrary(sparseSEM_dll)
    else:
        raise ValueError('loadEBglmnetLib not yet implemented for non-posix OS')