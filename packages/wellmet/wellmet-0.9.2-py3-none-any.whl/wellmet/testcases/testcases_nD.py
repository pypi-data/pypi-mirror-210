#!/usr/bin/env python
# coding: utf-8

#оӵ Тӧдьы кабъёс (ящикьёс) эскером

# every testcase from this module should take ndim parameter 

from .. import whitebox
from .. import g_models as gm
from .. import f_models
from .. import sball
import scipy.stats as stats

import numpy as np


beta_pf6 = -stats.norm.ppf(1e-6)

__all__ = []

#č zde ten __all__ těžko dohlídáme
#č budeme přidávat do seznamu postupně
def add(str):
    __all__.append(str)


# neverfall
add('snorm_neverfall')
def snorm_neverfall(ndim):
    return whitebox.WhiteBox(f_models.SNorm(ndim), gm.neverfall)


add('snorm_line_pf6')
def snorm_line_pf6(ndim):
    return whitebox.Line(ndim, -stats.norm.ppf(1e-6))
    
add('snorm_twoline_pf6')
def snorm_twoline_pf6(ndim):
    return whitebox.TwoLine(ndim, -stats.norm.ppf(1e-6 / 2))


# HyperRovina, куда ж без неё?
# Gauß
add('hyperplane_pf3')
def hyperplane_pf3(ndim):
    return whitebox.Gaussian_Z_sum(ndim, beta_exact=-stats.norm.ppf(1e-3))

add('hyperplane_pf6')
def hyperplane_pf6(ndim):
    return whitebox.Gaussian_Z_sum(ndim, beta_exact=beta_pf6)

add('lognorm_pprod_pf6')
def lognorm_pprod_pf6(ndim):
    return whitebox.Lognormal_Z_prod(ndim, beta_exact=beta_pf6)

add('lognorm_mprod_pf6')
def lognorm_mprod_pf6(ndim):
    return whitebox.Lognormal_Z_prod(ndim, beta_exact=beta_pf6, sign=-1)

add('snorm_max_pf6')
def snorm_max_pf6(ndim):
    return whitebox.Gaussian_Z_max(ndim=ndim, pf_exact=1e-6)

add('snorm_min_pf6')
def snorm_min_pf6(ndim):
    return whitebox.Gaussian_Z_min(ndim=ndim, pf_exact=1e-6)

""" parametry pravdepodobnostniho rozdeleni pro Z_min s Weib. velicinami
wb_scales=(1,1) - tuple of Weibull scale parameters, len(wb_scales)==nvar
shape = 5 
je třeba zadat buď pf_exact, nebo konštantu u funkce minima Z_min """
# g= min(X1, X2, X3, X4) + c
add('weibull_min_pf6')
def weibull_min_pf6(ndim):
    wb_scales = np.ones(ndim)
    return whitebox.Weibull_Z_min(wb_scales=wb_scales, shape=4, pf_exact=1e-6)
    #whitebox.Weibull_Z_min(wb_scales=(1.5,0.9), shape=4, pf_exact=1.0e-6)





# neither Gauß knows whats going on there
#whitebox.Gaussian_Z_sumexp(nvar=2, pf_exact=1.0e-6)




# je třeba zadat buď pf_exact, nebo konštantu u funkce Z_sumsq
# g = np.sum(sample**2, axis=1) - self._const
add('sumsq_pf6')
def sumsq_pf6(ndim):
    return whitebox.SNorm_Z_sumsq(ndim, pf_exact=1e-6)
    #whitebox.SNorm_Z_sumsq(nvar=2, pf_exact=1.0e-6)



# libustka
add('sball_pf6')
def sball_pf6(ndim):
    return whitebox.SNorm_S_ball(ndim, r=sball.get_Radius_pf(ndim, 1e-6))



