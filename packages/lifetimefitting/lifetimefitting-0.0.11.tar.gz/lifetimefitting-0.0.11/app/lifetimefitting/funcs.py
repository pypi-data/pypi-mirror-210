import numpy as np
def expFunc(t, I0, τ) -> float:
    return np.multiply(np.exp(np.negative(np.divide(t, τ))), I0)

def expFuncWC(t, I0, τ, c) -> float:
    return np.multiply(expFunc(t, I0, τ), c)

def expFuncx2(t, I0, τ_1, c_1, τ_2, c_2):
    return np.add(np.multiply(expFunc(t, I0, τ_1), c_1),
                  np.multiply(expFunc(t, I0, τ_2), c_2))

def expFuncx3(t, I0, τ_1, c_1, τ_2, c_2, τ_3, c_3):
    return np.add(np.add(np.multiply(expFunc(t, I0, τ_1), c_1),
                         np.multiply(expFunc(t, I0, τ_2), c_2)),
                  np.multiply(expFunc(t, I0, τ_3), c_3))

def expFuncx4(t, I0, τ_1, c_1, τ_2, c_2, τ_3, c_3, τ_4, c_4):
    return np.add(np.add(np.add(np.multiply(expFunc(t, I0, τ_1), c_1),
                                np.multiply(expFunc(t, I0, τ_2), c_2)),
                         np.multiply(expFunc(t, I0, τ_3), c_3)),
                  np.multiply(expFunc(t, I0, τ_4), c_4))

def linFunc(t, I0, τ) -> float:
    # return np.add(np.negative(np.divide(t, τ)), np.log(I0))
    return np.multiply(np.exp(np.negative(np.divide(t, τ))), I0)

def linFuncWC(t, I0, τ, c) -> float:
    return np.log(np.multiply(linFunc(t, I0, τ), c))

def linFuncx2(t, I0, τ_1, c_1, τ_2, c_2):
    return np.log(np.add(np.multiply(linFunc(t, I0, τ_1), c_1), 
                         np.multiply(linFunc(t, I0, τ_2), c_2)))

def linFuncx3(t, I0, τ_1, c_1, τ_2, c_2, τ_3, c_3):
    return np.log(np.add(np.add(np.multiply(linFunc(t, I0, τ_1), c_1),
                                np.multiply(linFunc(t, I0, τ_2), c_2)),
                         np.multiply(linFunc(t, I0, τ_3), c_3)))

def linFuncx4(t, I0, τ_1, c_1, τ_2, c_2, τ_3, c_3, τ_4, c_4):
    return np.log(np.add(np.add(np.add(np.multiply(linFunc(t, I0, τ_1), c_1), 
                                       np.multiply(linFunc(t, I0, τ_2), c_2)), 
                                np.multiply(linFunc(t, I0, τ_3), c_3)), 
                         np.multiply(linFunc(t, I0, τ_4), c_4)))
