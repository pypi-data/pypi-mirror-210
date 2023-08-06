import numpy as np
cimport numpy as cnp
from libc.math cimport sin, pi

cpdef cnp.ndarray sir(cnp.ndarray x, float t, float beta, float gamma): 
    cdef cnp.ndarray[cnp.float_t, ndim=1] dx

    cdef float s = x[0]
    cdef float i = x[1]
    cdef float r = x[2]

    cdef float ds = - beta * s * i
    cdef float di = + beta * s * i - gamma * i
    cdef float dr =                + gamma * i

    dx = np.array([ds,di,dr], dtype=float)
    return dx


cpdef cnp.ndarray sirs_vs(cnp.ndarray x, float t, float beta, float gamma, float alpha, float zeta, float xi): 
    cdef cnp.ndarray[cnp.float_t, ndim=1] dx
    
    cdef float s = x[0]
    cdef float i = x[1]
    cdef float r = x[2]

    cdef float _lambda = beta * (1 + xi * sin(2*pi*t/365))
    cdef float _eta    = zeta if s > zeta else s

    cdef float ds = - _lambda * s * i             - _eta + alpha * r
    cdef float di = + _lambda * s * i - gamma * i
    cdef float dr =                   + gamma * i + _eta - alpha * r 

    dx = np.array([ds,di,dr], dtype=float)
    return dx