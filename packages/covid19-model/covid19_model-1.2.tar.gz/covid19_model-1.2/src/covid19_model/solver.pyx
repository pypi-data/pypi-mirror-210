import numpy as np
cimport numpy as cnp

cpdef solve(model, x0, tspan, h, args):
    cdef cnp.ndarray[cnp.float_t, ndim=2] solution
    solution = np.empty(shape=(len(tspan), len(x0)))

    cdef int c = 0

    cdef cnp.ndarray[cnp.float_t, ndim=1] x
    cdef cnp.ndarray[cnp.float_t, ndim=1] dx

    x = x0
    solution[c] = x.copy()

    for t in tspan[1:]:
        c += 1
        dx = model(x, t, *args) * h
        x += dx
        solution[c] = x.copy()
    return solution