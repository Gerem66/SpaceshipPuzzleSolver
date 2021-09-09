from numba import jit, cuda
import numpy as np
from timeit import default_timer as timer

def func1(a):
    for i in range(10000000):
        a[i]+= 1

@jit
def func2(a):
    for i in range(10000000):
        a[i]+= 1

if __name__ == "__main__":
    n = 10000000
    a = np.ones(n, dtype = np.float64)

    start = timer()
    func1(a)
    print("without GPU:", timer()-start)

    start = timer()
    func2(a)
    print("with GPU:", timer()-start)