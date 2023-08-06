import numpy as np
from pyoperators import *
from scipy.optimize import minimize
import multiprocess as m
import time

class FitMultiProcessCPU:

    def __init__(self, chi2, nb_cpu, x0, method='TNC', tol=1e-20, options={}):

        self.nb_cpu = nb_cpu
        
        self.x0 = x0
        self.chi2 = chi2
        self.method = method
        self.tol = tol
        self.options = options


    def fit(self, args):

        res = minimize(self.chi2, self.x0, args=args, method=self.method, tol=self.tol, options=self.options)
        return res.x
    

    def perform(self, x):

        pool = m.Pool(processes=self.nb_cpu)
        results = pool.starmap(self.fit, [[param_values] for param_values in x])
        pool.close()
        pool.join()

        return np.concatenate(results)

