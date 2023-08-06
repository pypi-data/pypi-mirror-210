#!/usr/bin/env python
# coding: utf-8

"""
We will prepare here WhiteBox instances
of different well-known 2D problems
"""

import numpy as np
from .. import g_models as gm
from .. import f_models
from ..whitebox import WhiteBox
import scipy.stats as stats
from scipy import integrate # for Pareto tail

__all__ = [
            'uniform_branin_2D',
            'snorm_four_branch_2D',
            'snorm_four_branch_2D_2',
            'snorm_piecewise_2D_linear',
            'piecewise_pareto_tail',
            'snorm_min_2D_linear',
            'snorm_min_2D_logistic',
            'modified_rastrigin',
            'quadratic'
            ]

f = f_models.SNorm(2)
# Uniform-uniform
# from scipy: "In the standard form, the distribution is uniform on [0, 1]."
u = f_models.UnCorD((stats.uniform, stats.uniform))



"""
I would like to use function definitions to clearly isolate ones testcases
"""

# Rescaled Branin function
def uniform_branin_2D():
    wt = WhiteBox(u, gm.branin_2D)
    wt.pf_exact = 0.257
    wt.pf_exact_method = 'known value' #"some guys said me that" it's 0.256
    wt.description = "Rescaled Branin function"
    return wt

# Four branch system
def snorm_four_branch_2D():
    wt = WhiteBox(f, gm.FourBranch2D(k1=3, k2=7))
    wt.pf_exact = 2.34e-03
    wt.pf_exact_method = 'known value' #"some guys said me that" 
    wt.description = "Four branch system from some paper"
    return wt


def snorm_four_branch_2D_2():
    wt = WhiteBox(f, gm.FourBranch2D(k1=5.5, k2=11))
    # TODO calculate
    #wt.pf_exact = 0.257
    #wt.pf_exact_method = 'known value' #"some guys said me that" it's 0.256
    wt.description = "Four branch system from another paper"
    return wt





# Breitung
# Piecewise linear function
def snorm_piecewise_2D_linear():
    wt = WhiteBox(f, gm.piecewise_2D_linear)
    wt.description = "Breitung. Piecewise linear function"
    return wt



# Pareto tail
class PiecewiseParetoDist:
    def __init__(self, a=3.5):
        self.ax = a
        self.au = stats.norm.cdf(a) 
        self.c = np.log(stats.norm.cdf(-a))/np.log(a)
        self.pareto = stats.pareto(b=-self.c)
        # без излишевст
        self._p = integrate.quad(lambda x: self.pdf(x), -np.inf, np.inf)[0]
        self._mean = integrate.quad(lambda x: x*self.pdf(x), -np.inf, np.inf)[0]
        self._var = integrate.quad(lambda x: x**2*self.pdf(x), -np.inf, np.inf)[0]
        
    def cdf(self, x):
        return np.where(x < self.ax, stats.norm.cdf(x), self.pareto.cdf(x))
    def pdf(self, x):
        return np.where(x < self.ax, stats.norm.pdf(x), self.pareto.pdf(x))
    def ppf(self, u):
        return np.where(u < self.au, stats.norm.ppf(u), self.pareto.ppf(u))
        
    def mean(self): return self._mean
    def var(self): return self._var
    def std(self): return np.sqrt(self._var)
    


def piecewise_pareto_tail():
    h = f_models.UnCorD((stats.norm, PiecewiseParetoDist()))
    wt = WhiteBox(h, gm.non_chi_squares)
    wt.pf_exact = 1.87e-06
    wt.pf_exact_method = 'FORM-type thought-three beta points'
    wt.description = "Breitung. Pareto tail"
    return wt



# Logistic 2D function
def snorm_min_2D_linear():
    wt = WhiteBox(f, gm.Logistic2D())
    wt.description = "Breitung. 2D linear (easy version for SuS)"
    return wt

def snorm_min_2D_logistic():
    wt = WhiteBox(f, gm.Logistic2D(easy_version=False))
    wt.description = "Breitung. Logistic 2D function (hard version for SuS)"
    return wt

def modified_rastrigin():
    wt = WhiteBox(f, gm.modified_rastrigin)
    wt.description = "Modified Rastrigin"
    wt.pf_exact = 7.34e-02
    wt.pf_exact_method = 'known value'
    return wt

def quadratic():
    wt = WhiteBox(f, gm.quadratic)
    return wt
    
    



