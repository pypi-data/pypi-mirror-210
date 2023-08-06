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
    

    def perform_cpu(self, x):

        pool = m.Pool(processes=self.nb_cpu)
        results = pool.starmap(self.fit, [[param_values] for param_values in x])
        pool.close()
        pool.join()

        return np.concatenate(results)

class WrapperMPI:

    def __init__(self, comm, chi2, cpu_per_tasks, x0, method='TNC', tol=1e-3, options={}, verbose=False):

        #FitMultiProcessCPU.__init__(self, chi2, cpu_per_tasks, x0, method=method, tol=tol, options=options)

        ### MPI distribution
        self.comm = comm
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()
        if verbose:
            print(f'size = {self.size} and rank = {self.rank}')

        self.fit_multi_process = FitMultiProcessCPU(chi2, cpu_per_tasks, x0, method=method, tol=tol, options=options)
        self.nb_cpu = self.fit_multi_process.nb_cpu

    def _split_params(self, index_theta):
        return np.where(index_theta % self.size == self.rank)[0]
        
    def perform(self, index_theta):
        res = np.zeros(len(index_theta))
        index_per_process = self._split_params(index_theta)
        number_loop = len(index_per_process) // self.fit_multi_process.nb_cpu
        rest_loop = len(index_per_process) % self.fit_multi_process.nb_cpu

        for iloop in range(number_loop):
            
            res[index_per_process[iloop*self.nb_cpu:(iloop+1)*self.nb_cpu]] = self.fit_multi_process.perform_cpu(list(index_per_process[iloop*self.nb_cpu:(iloop+1)*self.nb_cpu]))
            
        res[index_per_process[-rest_loop:]] = self.fit_multi_process.perform_cpu(list(index_per_process[-rest_loop:]))
        
        return res