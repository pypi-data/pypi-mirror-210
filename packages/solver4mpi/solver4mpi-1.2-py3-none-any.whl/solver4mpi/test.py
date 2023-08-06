import pysm3
import pysm3.units as u
from pysm3 import utils
import healpy as hp
import matplotlib.pyplot as plt
from minimizer_multiprocess import *
import sys
import time
import pickle
from functools import partial
import os
sys.path.append('/Users/mregnier/Desktop/Libs/qubic/qubic/scripts/MapMaking')

import component_model as c
import mixing_matrix as mm

def _scale_components_1pix(beta, ipix, mref, allnus):

    components = c.Dust(nu0=nu0, temp=20)
    A_ev = mm.MixingMatrix(components).evaluator(allnus)
    Aev = A_ev(beta)
    nf, nc = Aev.shape
    m_nu = np.zeros((nf, 3))
    for i in range(3): #Nstk
        m_nu[:, i] = Aev @ np.array([mref[ipix, i]])

    return m_nu

nside = 16
sky=pysm3.Sky(nside=nside, preset_strings=['d0'], output_unit="uK_CMB")
nu0 = 150
mref = np.array(sky.get_emission(nu0 * u.GHz, None).T * utils.bandpass_unit_conversion(nu0*u.GHz, None, u.uK_CMB))


allnus = np.array([140, 150, 160])
m_nu = np.zeros((len(allnus), 12*nside**2, 3))

for j in range(12*nside**2):
    m_nu[:, j, :] = _scale_components_1pix(np.array([1.54]), j, mref, allnus)


def chi2(x, ipix, mref, m_nu, allnus):

    #map_beta[ipix] = x
    m_nu_fake = _scale_components_1pix(x, ipix, mref, allnus)
    
    return np.sum((m_nu_fake - m_nu[:, ipix, :])**2)

#val = chi2(np.array([1.54]), 0, A, mref, m_nu)
nb_cpu = os.cpu_count()
index_beta = np.arange(0, nb_cpu, 1)
chi2_partial = partial(chi2, mref=mref, m_nu=m_nu, allnus=allnus)
#val = chi2_partial(np.array([1.54]), 0)
#print(val)
beta_fit = FitMultiProcessCPU(chi2_partial, nb_cpu, x0=np.ones(1), method='L-BFGS-B', tol=1e-3).perform(list(index_beta))
print(beta_fit)